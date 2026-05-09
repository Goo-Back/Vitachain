"""
AI Service for VitaChain KATARA
Handles Claude API integration for agronomic recommendations
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import structlog
from fastapi import HTTPException, status
from anthropic import AsyncAnthropic
from app.models.schemas import (
    AIAnalysisRequest, AIRecommendation, TelemetrySummary,
    StructuredRecommendations, RecommendationItem, RecommendationPriority
)
from app.core.config import settings

logger = structlog.get_logger("ai_service")


class AIAnalysisTimeout(Exception):
    """AI analysis timeout exception"""
    pass


class AIAnalysisFailed(Exception):
    """AI analysis failed exception"""
    pass


class AIService:
    """Service for AI-powered agronomic analysis"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def analyze_device_telemetry(
        self, 
        device_id: str, 
        farmer_id: uuid.UUID, 
        analysis_request: AIAnalysisRequest,
        weather_data: Optional[Dict[str, Any]] = None,
        ndvi_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze telemetry data for a device using Claude AI
        
        Args:
            device_id: Device identifier
            farmer_id: Farmer ID from JWT token
            analysis_request: Analysis parameters
            
        Returns:
            Analysis job information
            
        Raises:
            HTTPException: If device not found, access denied, or analysis fails
        """
        try:
            logger.info("Starting AI analysis", device_id=device_id, farmer_id=str(farmer_id))
            
            # Verify device ownership
            device = await self._verify_device_ownership(device_id, farmer_id)
            
            # Get telemetry data for analysis
            telemetry_data = await self._get_telemetry_data(
                device_id, 
                analysis_request.start_date, 
                analysis_request.end_date
            )
            
            if not telemetry_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "NO_TELEMETRY_DATA",
                        "message": "No telemetry data found for analysis period"
                    }
                )
            
            # Generate analysis ID
            analysis_id = uuid.uuid4()
            
            # Start async analysis
            asyncio.create_task(
                self._perform_ai_analysis(
                    analysis_id, 
                    device_id, 
                    farmer_id, 
                    telemetry_data, 
                    analysis_request,
                    weather_data
                )
            )
            
            return {
                "analysis_id": analysis_id,
                "status": "processing",
                "estimated_completion": datetime.utcnow() + timedelta(seconds=30)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error in AI analysis", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
    
    async def get_recommendations(
        self, 
        device_id: str, 
        farmer_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AIRecommendation]:
        """
        Get AI recommendations for a device
        
        Args:
            device_id: Device identifier
            farmer_id: Farmer ID from JWT token
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of AI recommendations
            
        Raises:
            HTTPException: If device not found or access denied
        """
        try:
            logger.info("Fetching AI recommendations", device_id=device_id, farmer_id=str(farmer_id))
            
            # Verify device ownership
            await self._verify_device_ownership(device_id, farmer_id)
            
            # Query recommendations
            query = self.supabase.table('ai_recommendations').select('*').eq('device_id', device_id)
            
            if start_date:
                query = query.gte('created_at', start_date.isoformat())
            if end_date:
                query = query.lte('created_at', end_date.isoformat())
            
            result = query.order('created_at', desc=True).execute()
            
            if not result.data:
                return []
            
            # Convert to AIRecommendation objects
            recommendations = []
            for rec in result.data:
                recommendations.append(self._map_to_recommendation(rec))
            
            return recommendations
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error fetching recommendations", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
    
    async def _verify_device_ownership(self, device_id: str, farmer_id: uuid.UUID) -> Dict[str, Any]:
        """Verify that the farmer owns the device"""
        result = self.supabase.table('iot_devices').select('*').eq('device_id', device_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DEVICE_NOT_FOUND",
                    "message": "Device not found"
                }
            )
        
        device = result.data[0]
        if device['farmer_id'] != str(farmer_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Access denied to this device"
                }
            )
        
        return device
    
    async def _get_telemetry_data(
        self, 
        device_id: str, 
        start_date: Optional[datetime], 
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Get telemetry data for analysis period"""
        query = self.supabase.table('telemetry_readings').select('*').eq('device_id', device_id)
        
        if start_date:
            query = query.gte('timestamp', start_date.isoformat())
        if end_date:
            query = query.lte('timestamp', end_date.isoformat())
        
        # Default to last 7 days if no dates provided
        if not start_date and not end_date:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            query = self.supabase.table('telemetry_readings').select('*').eq('device_id', device_id).gte('timestamp', start_date.isoformat()).lte('timestamp', end_date.isoformat())
        
        result = query.order('timestamp', desc=True).limit(1000).execute()
        return result.data if result.data else []
    
    async def _get_latest_ndvi_data(self, device_id: str, farmer_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get latest NDVI data for enhanced AI analysis"""
        try:
            # Get the most recent NDVI reading for the device
            result = self.supabase.table('ndvi_readings').select('*').eq('device_id', device_id).eq('farmer_id', str(farmer_id)).order('created_at', desc=True).limit(1).execute()
            
            if not result.data:
                return None
            
            ndvi_reading = result.data[0]
            
            # Format NDVI data for AI prompt
            return {
                "current": {
                    "ndvi_value": ndvi_reading["ndvi_value"],
                    "ndvi_trend": ndvi_reading["ndvi_trend"],
                    "vegetation_health": self._assess_vegetation_health(ndvi_reading["ndvi_value"]),
                    "data_quality": ndvi_reading["data_quality"],
                    "cloud_cover": ndvi_reading["cloud_cover"],
                    "acquisition_date": ndvi_reading["acquisition_date"]
                },
                "trend": {
                    "ndvi_30d_avg": ndvi_reading["ndvi_value"],  # Simplified - would calculate from historical data
                    "trend_direction": ndvi_reading["ndvi_trend"],
                    "stress_detected": ndvi_reading["ndvi_value"] < 0.3
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to get NDVI data for AI analysis: {str(e)}")
            return None
    
    def _assess_vegetation_health(self, ndvi_value: float) -> str:
        """Assess vegetation health based on NDVI value"""
        if ndvi_value >= 0.4:
            return "good"
        elif ndvi_value >= 0.3:
            return "moderate"
        elif ndvi_value >= 0.2:
            return "poor"
        else:
            return "critical"
    
    async def _perform_ai_analysis(
        self,
        analysis_id: uuid.UUID,
        device_id: str,
        farmer_id: uuid.UUID,
        telemetry_data: List[Dict[str, Any]],
        analysis_request: AIAnalysisRequest,
        weather_data: Optional[Dict[str, Any]] = None
    ):
        """Perform the actual AI analysis using Claude API"""
        try:
            logger.info("Performing AI analysis", analysis_id=str(analysis_id))
            
            # Get device location for context
            device_result = self.supabase.table('iot_devices').select('location_lat, location_lng').eq('device_id', device_id).execute()
            location = None
            if device_result.data:
                device = device_result.data[0]
                if device['location_lat'] and device['location_lng']:
                    location = (device['location_lat'], device['location_lng'])
            
            # Aggregate telemetry data
            telemetry_summary = self._aggregate_telemetry(telemetry_data)
            
            # Try to get NDVI data for enhanced analysis
            ndvi_data = await self._get_latest_ndvi_data(device_id, farmer_id)
            
            # Generate AI prompt with weather and NDVI context
            prompt = self._generate_ai_prompt(telemetry_summary, location, analysis_request.analysis_type, weather_data, ndvi_data)
            
            # Call Claude API with timeout
            try:
                response = await asyncio.wait_for(
                    self.anthropic_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": prompt}]
                    ),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.error("Claude API timeout", analysis_id=str(analysis_id))
                raise AIAnalysisTimeout("Claude API analysis timed out after 30 seconds")
            
            # Parse AI response
            ai_response_text = response.content[0].text
            structured_recommendations = self._parse_ai_response(ai_response_text)
            
            # Store recommendation
            recommendation_record = {
                "id": str(analysis_id),
                "device_id": device_id,
                "farmer_id": str(farmer_id),
                "analysis_period_start": analysis_request.start_date.isoformat() if analysis_request.start_date else None,
                "analysis_period_end": analysis_request.end_date.isoformat() if analysis_request.end_date else None,
                "telemetry_summary": telemetry_summary,
                "ai_response": ai_response_text,
                "recommendations": structured_recommendations.dict(),
                "confidence_score": self._calculate_confidence_score(structured_recommendations),
                "analysis_type": analysis_request.analysis_type.value,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('ai_recommendations').insert(recommendation_record).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error("Failed to store recommendation", error=result.error)
                raise AIAnalysisFailed("Failed to store AI recommendation")
            
            logger.info("AI analysis completed successfully", analysis_id=str(analysis_id))
            
        except AIAnalysisTimeout:
            # Store failed analysis record
            await self._store_failed_analysis(analysis_id, device_id, farmer_id, "timeout")
        except AIAnalysisFailed:
            # Store failed analysis record
            await self._store_failed_analysis(analysis_id, device_id, farmer_id, "failed")
        except Exception as e:
            logger.error("Unexpected error in AI analysis", error=str(e))
            await self._store_failed_analysis(analysis_id, device_id, farmer_id, "error")
    
    def _aggregate_telemetry(self, telemetry_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate telemetry data for analysis"""
        if not telemetry_data:
            return {}
        
        temperatures = [float(t['temperature']) for t in telemetry_data if t.get('temperature')]
        humidities = [float(t['humidity']) for t in telemetry_data if t.get('humidity')]
        ndvi_values = [float(t['ndvi']) for t in telemetry_data if t.get('ndvi')]
        
        # Calculate NDVI trend
        ndvi_trend = "stable"
        if len(ndvi_values) > 1:
            recent_avg = sum(ndvi_values[:10]) / min(10, len(ndvi_values))
            older_avg = sum(ndvi_values[-10:]) / min(10, len(ndvi_values))
            if recent_avg > older_avg + 0.05:
                ndvi_trend = "increasing"
            elif recent_avg < older_avg - 0.05:
                ndvi_trend = "decreasing"
        
        return {
            "avg_temperature": sum(temperatures) / len(temperatures) if temperatures else 0,
            "avg_humidity": sum(humidities) / len(humidities) if humidities else 0,
            "ndvi_trend": ndvi_trend,
            "data_points": len(telemetry_data),
            "min_temperature": min(temperatures) if temperatures else 0,
            "max_temperature": max(temperatures) if temperatures else 0,
            "min_humidity": min(humidities) if humidities else 0,
            "max_humidity": max(humidities) if humidities else 0
        }
    
    def _generate_ai_prompt(
        self, 
        telemetry_summary: Dict[str, Any], 
        location: Optional[Tuple[float, float]], 
        analysis_type: str,
        weather_data: Optional[Dict[str, Any]] = None,
        ndvi_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate AI prompt for Claude"""
        
        # Get Moroccan context
        moroccan_context = self._get_moroccan_context(location)
        
        base_prompt = f"""
As an expert agronomist specializing in Moroccan agriculture, analyze the following IoT sensor data:

Location: {location[0]}, {location[1] if location else 'Unknown'} (Morocco)
Climate Zone: {moroccan_context['climate_zone']}
Season: {moroccan_context['current_season']}
Common Crops: {', '.join(moroccan_context['common_crops'])}

Data Period: Last {telemetry_summary.get('data_points', 0)} readings

Telemetry Summary:
- Average Temperature: {telemetry_summary.get('avg_temperature', 0):.1f}°C
- Average Humidity: {telemetry_summary.get('avg_humidity', 0):.1f}%
- NDVI Trend: {telemetry_summary.get('ndvi_trend', 'stable')}
- Temperature Range: {telemetry_summary.get('min_temperature', 0):.1f}°C to {telemetry_summary.get('max_temperature', 0):.1f}°C
- Humidity Range: {telemetry_summary.get('min_humidity', 0):.1f}% to {telemetry_summary.get('max_humidity', 0):.1f}%

Regional Context:
- Climate Challenges: {', '.join(moroccan_context['seasonal_challenges'])}
- Water Scarcity: {moroccan_context['water_scarcity_considerations']}
- Soil Types: {', '.join(moroccan_context['soil_types'])}
"""
        
        # Add weather context if available
        if weather_data:
            current = weather_data.get('current', {})
            forecast = weather_data.get('forecast', [])
            
            weather_context = f"""
Weather Conditions (Current):
- Temperature: {current.get('temperature', 'N/A')}°C
- Humidity: {current.get('humidity', 'N/A')}%
- Rainfall (24h): {current.get('rainfall_24h', 'N/A')}mm
- Wind Speed: {current.get('wind_speed', 'N/A')}m/s
- Weather: {current.get('weather_description', 'N/A')}

Weather Forecast (Next 24h):
"""
            for i, forecast_point in enumerate(forecast[:4]):  # Show next 4 forecast points
                forecast_time = forecast_point.get('time', 'Unknown')
                temp = forecast_point.get('temperature', 'N/A')
                rain_prob = forecast_point.get('rain_probability', 'N/A')
                weather_main = forecast_point.get('weather_main', 'N/A')
                weather_context += f"- {forecast_time}: {temp}°C, {rain_prob}% rain, {weather_main}\n"
            
            weather_context += """
Weather Impact on Farming:
"""
            # Add specific weather impact analysis
            temp = current.get('temperature', 0)
            rainfall_24h = current.get('rainfall_24h', 0)
            wind_speed = current.get('wind_speed', 0)
            
            if temp > 35:
                weather_context += "- High temperatures increase water demand and heat stress risk\n"
            if temp < 5:
                weather_context += "- Low temperatures may slow crop growth\n"
            if rainfall_24h > 10:
                weather_context += "- Recent rainfall may reduce irrigation needs\n"
            if rainfall_24h == 0 and temp > 30:
                weather_context += "- No recent rainfall with high temperatures indicates drought risk\n"
            if wind_speed > 5:
                weather_context += "- High winds may affect pesticide application efficiency\n"
            
            base_prompt += weather_context
        
        # Add NDVI context if available
        if ndvi_data:
            current = ndvi_data.get('current', {})
            trend = ndvi_data.get('trend', {})
            
            ndvi_context = f"""
Satellite NDVI Analysis (Current):
- NDVI Value: {current.get('ndvi_value', 'N/A')}
- Vegetation Health: {current.get('vegetation_health', 'N/A')}
- NDVI Trend (30d): {trend.get('trend_direction', 'N/A')}
- Data Quality: {current.get('data_quality', 'N/A')}
- Cloud Cover: {current.get('cloud_cover', 'N/A')}%
- Acquisition Date: {current.get('acquisition_date', 'N/A')}

Vegetation Health Impact:
"""
            # Add specific NDVI impact analysis
            ndvi_value = current.get('ndvi_value', 0)
            trend_direction = trend.get('trend_direction', 'stable')
            stress_detected = trend.get('stress_detected', False)
            
            if ndvi_value >= 0.4:
                ndvi_context += "- Healthy vegetation detected - continue current practices\n"
            elif 0.3 <= ndvi_value < 0.4:
                ndvi_context += "- Moderate vegetation stress - review irrigation and nutrients\n"
            elif ndvi_value < 0.3:
                ndvi_context += "- Significant vegetation stress - immediate intervention needed\n"
            
            if trend_direction == "declining":
                ndvi_context += "- Declining NDVI trend - investigate potential causes\n"
            elif trend_direction == "improving":
                ndvi_context += "- Improving NDVI trend - current practices are effective\n"
            
            if stress_detected:
                ndvi_context += "- Vegetation stress detected - prioritize health interventions\n"
            
            ndvi_context += """
NDVI-Enhanced Recommendations:
"""
            base_prompt += ndvi_context
        
        if analysis_type == "irrigation":
            base_prompt += """
Focus specifically on irrigation recommendations:
1. Optimal watering schedule and frequency
2. Water conservation techniques
3. Soil moisture management
4. Drought mitigation strategies
"""
        elif analysis_type == "health":
            base_prompt += """
Focus specifically on crop health recommendations:
1. Disease and pest prevention
2. Nutrient deficiencies
3. Stress factors identification
4. Treatment recommendations
"""
        elif analysis_type == "soil":
            base_prompt += """
Focus specifically on soil management recommendations:
1. Soil health improvement
2. Fertilization schedule
3. Soil conservation practices
4. Organic matter enhancement
"""
        else:
            base_prompt += """
Provide comprehensive recommendations covering:
1. Irrigation scheduling and water management
2. Crop health monitoring and interventions  
3. Soil conservation and fertilization
4. Pest and disease prevention
"""
        
        base_prompt += """

Format your response as structured JSON with the following format:
{
  "irrigation": {
    "priority": "high|medium|low",
    "action": "Specific actionable recommendation",
    "reasoning": "Why this action is needed"
  },
  "crop_health": {
    "priority": "high|medium|low", 
    "action": "Specific actionable recommendation",
    "reasoning": "Why this action is needed"
  },
  "soil_management": {
    "priority": "high|medium|low",
    "action": "Specific actionable recommendation", 
    "reasoning": "Why this action is needed"
  },
  "pest_control": {
    "priority": "high|medium|low",
    "action": "Specific actionable recommendation",
    "reasoning": "Why this action is needed"
  }
}

Consider Moroccan climate conditions, water scarcity, and local agricultural practices in your recommendations.
"""
        
        return base_prompt
    
    def _get_moroccan_context(self, location: Optional[Tuple[float, float]]) -> Dict[str, Any]:
        """Get Moroccan agricultural context based on location"""
        # Default context for Morocco
        context = {
            "climate_zone": "Mediterranean",
            "current_season": self._get_current_season(),
            "common_crops": ["citrus", "olives", "vegetables", "cereals", "legumes"],
            "seasonal_challenges": ["water scarcity", "heat stress", "soil erosion"],
            "water_scarcity_considerations": "Prioritize drought-resistant crops and efficient irrigation",
            "soil_types": ["clay", "sandy loam", "calcareous"]
        }
        
        # Adjust based on location if available
        if location:
            lat, lng = location
            
            # Northern Morocco (Mediterranean)
            if lat > 34.0:
                context["climate_zone"] = "Mediterranean"
                context["common_crops"] = ["citrus", "olives", "vegetables", "strawberries"]
                context["seasonal_challenges"] = ["high humidity", "frost risk", "coastal winds"]
            
            # Central Morocco (Atlantic/Continental)
            elif 32.0 <= lat <= 34.0:
                context["climate_zone"] = "Continental"
                context["common_crops"] = ["cereals", "legumes", "olives", "almonds"]
                context["seasonal_challenges"] = ["temperature extremes", "limited rainfall", "soil degradation"]
            
            # Southern Morocco (Arid/Semi-arid)
            elif lat < 32.0:
                context["climate_zone"] = "Arid"
                context["common_crops"] = ["dates", "argan", "drought-tolerant vegetables"]
                context["seasonal_challenges"] = ["extreme heat", "water scarcity", "desertification"]
                context["water_scarcity_considerations"] = "Critical water conservation, drip irrigation essential"
        
        return context
    
    def _get_current_season(self) -> str:
        """Get current agricultural season in Morocco"""
        month = datetime.utcnow().month
        
        if 3 <= month <= 5:
            return "spring (planting season)"
        elif 6 <= month <= 8:
            return "summer (growing season, high heat)"
        elif 9 <= month <= 11:
            return "autumn (harvest season)"
        else:
            return "winter (dormant/cool season)"
    
    def _parse_ai_response(self, ai_response_text: str) -> StructuredRecommendations:
        """Parse Claude AI response into structured recommendations"""
        try:
            # Try to extract JSON from response
            import re
            
            # Look for JSON block in response
            json_match = re.search(r'\{[\s\S]*\}', ai_response_text)
            if json_match:
                json_str = json_match.group(0)
                recommendations_data = json.loads(json_str)
            else:
                # Fallback: create basic recommendations from text
                recommendations_data = self._create_fallback_recommendations(ai_response_text)
            
            # Convert to RecommendationItem objects
            recommendations = StructuredRecommendations()
            
            for category, rec_data in recommendations_data.items():
                if isinstance(rec_data, dict) and all(key in rec_data for key in ['priority', 'action', 'reasoning']):
                    rec_item = RecommendationItem(
                        priority=RecommendationPriority(rec_data['priority']),
                        action=rec_data['action'],
                        reasoning=rec_data['reasoning']
                    )
                    setattr(recommendations, category, rec_item)
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to parse AI response", error=str(e))
            # Return empty recommendations on parse failure
            return StructuredRecommendations()
    
    def _create_fallback_recommendations(self, ai_response_text: str) -> Dict[str, Any]:
        """Create fallback recommendations from text response"""
        # Simple keyword-based extraction for fallback
        recommendations = {}
        
        if "irrigation" in ai_response_text.lower() or "water" in ai_response_text.lower():
            recommendations["irrigation"] = {
                "priority": "medium",
                "action": "Review irrigation schedule based on current conditions",
                "reasoning": "AI analysis indicates irrigation considerations needed"
            }
        
        if "health" in ai_response_text.lower() or "disease" in ai_response_text.lower():
            recommendations["crop_health"] = {
                "priority": "medium", 
                "action": "Monitor crop health for signs of stress or disease",
                "reasoning": "AI analysis indicates crop health considerations needed"
            }
        
        if "soil" in ai_response_text.lower() or "fertil" in ai_response_text.lower():
            recommendations["soil_management"] = {
                "priority": "low",
                "action": "Assess soil conditions and nutrient levels",
                "reasoning": "AI analysis indicates soil management considerations"
            }
        
        return recommendations
    
    def _calculate_confidence_score(self, recommendations: StructuredRecommendations) -> float:
        """Calculate confidence score based on recommendation completeness"""
        score = 0.0
        total_categories = 4
        
        if recommendations.irrigation:
            score += 0.25
        if recommendations.crop_health:
            score += 0.25
        if recommendations.soil_management:
            score += 0.25
        if recommendations.pest_control:
            score += 0.25
        
        return min(score, 1.0)
    
    def _map_to_recommendation(self, rec_data: Dict[str, Any]) -> AIRecommendation:
        """Map database record to AIRecommendation object"""
        # Parse telemetry summary
        telemetry_summary = TelemetrySummary(**rec_data['telemetry_summary'])
        
        # Parse structured recommendations
        recommendations_dict = rec_data.get('recommendations', {})
        structured_recommendations = StructuredRecommendations()
        
        for category, rec_item_data in recommendations_dict.items():
            if rec_item_data:
                rec_item = RecommendationItem(
                    priority=RecommendationPriority(rec_item_data['priority']),
                    action=rec_item_data['action'],
                    reasoning=rec_item_data['reasoning']
                )
                setattr(structured_recommendations, category, rec_item)
        
        return AIRecommendation(
            id=uuid.UUID(rec_data['id']),
            device_id=rec_data['device_id'],
            analysis_period={
                "start": rec_data['analysis_period_start'],
                "end": rec_data['analysis_period_end']
            },
            telemetry_summary=telemetry_summary,
            ai_response=rec_data['ai_response'],
            recommendations=structured_recommendations,
            confidence_score=rec_data['confidence_score'],
            created_at=datetime.fromisoformat(rec_data['created_at'].replace('Z', '+00:00'))
        )
    
    async def _store_failed_analysis(
        self, 
        analysis_id: uuid.UUID, 
        device_id: str, 
        farmer_id: uuid.UUID, 
        failure_type: str
    ):
        """Store failed analysis record"""
        try:
            failed_record = {
                "id": str(analysis_id),
                "device_id": device_id,
                "farmer_id": str(farmer_id),
                "telemetry_summary": {},
                "ai_response": f"Analysis failed: {failure_type}",
                "recommendations": {},
                "confidence_score": 0.0,
                "analysis_type": "comprehensive",
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table('ai_recommendations').insert(failed_record).execute()
            
        except Exception as e:
            logger.error("Failed to store failed analysis record", error=str(e))
