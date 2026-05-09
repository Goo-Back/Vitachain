"""
Tests for AI Recommendations Service
Comprehensive test coverage for AI agronomic recommendations functionality
"""

import pytest
import uuid
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException, status

from app.services.ai_service import AIService, AIAnalysisTimeout, AIAnalysisFailed
from app.models.schemas import (
    AIAnalysisRequest, AnalysisType, RecommendationPriority,
    AIRecommendation, TelemetrySummary, StructuredRecommendations,
    RecommendationItem
)


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    supabase = Mock()
    supabase.table = Mock()
    return supabase


@pytest.fixture
def sample_farmer_id():
    """Sample farmer ID for testing"""
    return uuid.uuid4()


@pytest.fixture
def sample_device_id():
    """Sample device ID for testing"""
    return "katara-550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def sample_telemetry_data():
    """Sample telemetry data for testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "farmer_id": str(uuid.uuid4()),
            "temperature": 32.5,
            "humidity": 45.2,
            "ndvi": 0.42,
            "battery_level": 78.5,
            "timestamp": "2026-05-03T14:30:00Z"
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "farmer_id": str(uuid.uuid4()),
            "temperature": 35.8,
            "humidity": 38.1,
            "ndvi": 0.38,
            "battery_level": 75.2,
            "timestamp": "2026-05-03T15:30:00Z"
        }
    ]


@pytest.fixture
def sample_device_record():
    """Sample device record for testing"""
    return {
        "id": str(uuid.uuid4()),
        "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
        "farmer_id": str(uuid.uuid4()),
        "name": "Parcelle Nord",
        "location_lat": 33.5,
        "location_lng": -7.6,
        "registered_at": "2026-05-01T10:00:00Z"
    }


@pytest.fixture
def ai_service(mock_supabase):
    """AI service instance for testing"""
    with patch('app.services.ai_service.settings'):
        return AIService(mock_supabase)


class TestAIServiceAnalyzeDeviceTelemetry:
    """Test AI analysis endpoint"""
    
    @pytest.mark.asyncio
    async def test_successful_analysis_request(
        self, ai_service, mock_supabase, sample_farmer_id, sample_device_id, 
        sample_device_record, sample_telemetry_data
    ):
        """Test successful AI analysis request"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_device_record]
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.limit.return_value.execute.return_value.data = sample_telemetry_data
        
        # Mock Claude API
        with patch.object(ai_service.anthropic_client, 'messages') as mock_messages:
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = json.dumps({
                "irrigation": {
                    "priority": "high",
                    "action": "Increase irrigation frequency",
                    "reasoning": "High temperatures detected"
                },
                "crop_health": {
                    "priority": "medium",
                    "action": "Monitor for stress",
                    "reasoning": "NDVI declining"
                }
            })
            mock_messages.create.return_value = mock_response
            
            # Mock database insert
            mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": str(uuid.uuid4())}]
            
            # Test request
            analysis_request = AIAnalysisRequest(
                analysis_type=AnalysisType.COMPREHENSIVE
            )
            
            result = await ai_service.analyze_device_telemetry(
                sample_device_id, 
                sample_farmer_id, 
                analysis_request
            )
            
            # Assertions
            assert result["status"] == "processing"
            assert "analysis_id" in result
            assert "estimated_completion" in result
            
            # Verify Claude API was called
            mock_messages.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_device_not_found(self, ai_service, mock_supabase, sample_farmer_id, sample_device_id):
        """Test analysis request for non-existent device"""
        # Setup mock
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        analysis_request = AIAnalysisRequest()
        
        with pytest.raises(HTTPException) as exc_info:
            await ai_service.analyze_device_telemetry(
                sample_device_id, 
                sample_farmer_id, 
                analysis_request
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["code"] == "DEVICE_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_access_denied(self, ai_service, mock_supabase, sample_device_id, sample_device_record):
        """Test analysis request for device owned by different farmer"""
        # Setup mock - device exists but belongs to different farmer
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_device_record]
        
        wrong_farmer_id = uuid.uuid4()
        analysis_request = AIAnalysisRequest()
        
        with pytest.raises(HTTPException) as exc_info:
            await ai_service.analyze_device_telemetry(
                sample_device_id, 
                wrong_farmer_id, 
                analysis_request
            )
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "FORBIDDEN"
    
    @pytest.mark.asyncio
    async def test_no_telemetry_data(self, ai_service, mock_supabase, sample_farmer_id, sample_device_id, sample_device_record):
        """Test analysis request with no telemetry data"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_device_record]
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        
        analysis_request = AIAnalysisRequest()
        
        with pytest.raises(HTTPException) as exc_info:
            await ai_service.analyze_device_telemetry(
                sample_device_id, 
                sample_farmer_id, 
                analysis_request
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["code"] == "NO_TELEMETRY_DATA"
    
    @pytest.mark.asyncio
    async def test_claude_api_timeout(self, ai_service, mock_supabase, sample_farmer_id, sample_device_id, sample_device_record, sample_telemetry_data):
        """Test Claude API timeout handling"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_device_record]
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.limit.return_value.execute.return_value.data = sample_telemetry_data
        
        # Mock Claude API timeout
        with patch.object(ai_service.anthropic_client, 'messages') as mock_messages:
            mock_messages.create.side_effect = asyncio.TimeoutError()
            
            # Mock failed analysis storage
            mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": str(uuid.uuid4())}]
            
            analysis_request = AIAnalysisRequest()
            
            # Should not raise exception - timeout is handled gracefully
            result = await ai_service.analyze_device_telemetry(
                sample_device_id, 
                sample_farmer_id, 
                analysis_request
            )
            
            assert result["status"] == "processing"


class TestAIServiceGetRecommendations:
    """Test getting AI recommendations"""
    
    @pytest.mark.asyncio
    async def test_get_recommendations_success(
        self, ai_service, mock_supabase, sample_farmer_id, sample_device_id, sample_device_record
    ):
        """Test successful retrieval of recommendations"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_device_record]
        
        sample_recommendation = {
            "id": str(uuid.uuid4()),
            "device_id": sample_device_id,
            "farmer_id": str(sample_farmer_id),
            "analysis_period_start": "2026-04-20T00:00:00Z",
            "analysis_period_end": "2026-04-27T00:00:00Z",
            "telemetry_summary": {
                "avg_temperature": 32.5,
                "avg_humidity": 45.2,
                "ndvi_trend": "declining",
                "data_points": 100,
                "min_temperature": 25.0,
                "max_temperature": 40.0,
                "min_humidity": 30.0,
                "max_humidity": 60.0
            },
            "ai_response": "Based on the telemetry data analysis...",
            "recommendations": {
                "irrigation": {
                    "priority": "high",
                    "action": "Increase irrigation frequency",
                    "reasoning": "High temperatures detected"
                }
            },
            "confidence_score": 0.87,
            "analysis_type": "comprehensive",
            "created_at": "2026-05-03T14:30:00Z"
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.select.return_value.order.return_value.execute.return_value.data = [sample_recommendation]
        
        recommendations = await ai_service.get_recommendations(
            sample_device_id, 
            sample_farmer_id
        )
        
        assert len(recommendations) == 1
        assert recommendations[0].device_id == sample_device_id
        assert recommendations[0].confidence_score == 0.87
    
    @pytest.mark.asyncio
    async def test_get_recommendations_with_date_filters(
        self, ai_service, mock_supabase, sample_farmer_id, sample_device_id, sample_device_record
    ):
        """Test getting recommendations with date filters"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_device_record]
        mock_supabase.table.return_value.select.return_value.eq.return_value.select.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = []
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        recommendations = await ai_service.get_recommendations(
            sample_device_id, 
            sample_farmer_id,
            start_date,
            end_date
        )
        
        assert len(recommendations) == 0
    
    @pytest.mark.asyncio
    async def test_get_recommendations_device_not_found(self, ai_service, mock_supabase, sample_farmer_id, sample_device_id):
        """Test getting recommendations for non-existent device"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        with pytest.raises(HTTPException) as exc_info:
            await ai_service.get_recommendations(sample_device_id, sample_farmer_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["code"] == "DEVICE_NOT_FOUND"


class TestAIServiceHelperMethods:
    """Test AI service helper methods"""
    
    def test_aggregate_telemetry(self, ai_service, sample_telemetry_data):
        """Test telemetry data aggregation"""
        result = ai_service._aggregate_telemetry(sample_telemetry_data)
        
        assert result["data_points"] == 2
        assert result["avg_temperature"] == 34.15  # (32.5 + 35.8) / 2
        assert result["avg_humidity"] == 41.65   # (45.2 + 38.1) / 2
        assert result["min_temperature"] == 32.5
        assert result["max_temperature"] == 35.8
        assert result["min_humidity"] == 38.1
        assert result["max_humidity"] == 45.2
    
    def test_aggregate_empty_telemetry(self, ai_service):
        """Test aggregation with empty telemetry data"""
        result = ai_service._aggregate_telemetry([])
        
        assert result["data_points"] == 0
        assert result["avg_temperature"] == 0
        assert result["avg_humidity"] == 0
    
    def test_parse_ai_response_success(self, ai_service):
        """Test successful AI response parsing"""
        ai_response = json.dumps({
            "irrigation": {
                "priority": "high",
                "action": "Increase irrigation frequency",
                "reasoning": "High temperatures detected"
            },
            "crop_health": {
                "priority": "medium",
                "action": "Monitor for stress",
                "reasoning": "NDVI declining"
            }
        })
        
        result = ai_service._parse_ai_response(ai_response)
        
        assert isinstance(result, StructuredRecommendations)
        assert result.irrigation is not None
        assert result.irrigation.priority == RecommendationPriority.HIGH
        assert result.irrigation.action == "Increase irrigation frequency"
        assert result.crop_health is not None
        assert result.crop_health.priority == RecommendationPriority.MEDIUM
    
    def test_parse_ai_response_fallback(self, ai_service):
        """Test AI response parsing with fallback"""
        ai_response = "Based on the analysis, irrigation should be increased due to high temperatures. Crop health monitoring is also recommended."
        
        result = ai_service._parse_ai_response(ai_response)
        
        assert isinstance(result, StructuredRecommendations)
        # Should have fallback recommendations based on keywords
        assert result.irrigation is not None
        assert result.irrigation.priority == RecommendationPriority.MEDIUM
    
    def test_calculate_confidence_score(self, ai_service):
        """Test confidence score calculation"""
        recommendations = StructuredRecommendations(
            irrigation=RecommendationItem(
                priority=RecommendationPriority.HIGH,
                action="Test action",
                reasoning="Test reasoning"
            ),
            crop_health=RecommendationItem(
                priority=RecommendationPriority.MEDIUM,
                action="Test action",
                reasoning="Test reasoning"
            )
        )
        
        score = ai_service._calculate_confidence_score(recommendations)
        assert score == 0.5  # 2 out of 4 categories filled
    
    def test_get_moroccan_context_northern(self, ai_service):
        """Test Moroccan context for northern region"""
        context = ai_service._get_moroccan_context((35.0, -5.0))
        
        assert context["climate_zone"] == "Mediterranean"
        assert "citrus" in context["common_crops"]
        assert "high humidity" in context["seasonal_challenges"]
    
    def test_get_moroccan_context_southern(self, ai_service):
        """Test Moroccan context for southern region"""
        context = ai_service._get_moroccan_context((30.0, -8.0))
        
        assert context["climate_zone"] == "Arid"
        assert "dates" in context["common_crops"]
        assert "extreme heat" in context["seasonal_challenges"]
        assert "Critical water conservation" in context["water_scarcity_considerations"]
    
    def test_get_current_season(self, ai_service):
        """Test current season detection"""
        with patch('app.services.ai_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.month = 5
            season = ai_service._get_current_season()
            assert season == "spring (planting season)"
            
            mock_datetime.utcnow.return_value.month = 8
            season = ai_service._get_current_season()
            assert season == "summer (growing season, high heat)"


class TestAIServiceErrorHandling:
    """Test AI service error handling"""
    
    @pytest.mark.asyncio
    async def test_claude_api_timeout_handling(self, ai_service):
        """Test Claude API timeout handling"""
        with patch.object(ai_service, '_store_failed_analysis') as mock_store:
            mock_store.return_value = None
            
            await ai_service._store_failed_analysis(
                uuid.uuid4(),
                "test_device",
                uuid.uuid4(),
                "timeout"
            )
            
            mock_store.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_map_to_recommendation(self, ai_service):
        """Test mapping database record to AIRecommendation"""
        rec_data = {
            "id": str(uuid.uuid4()),
            "device_id": "test_device",
            "analysis_period_start": "2026-04-20T00:00:00Z",
            "analysis_period_end": "2026-04-27T00:00:00Z",
            "telemetry_summary": {
                "avg_temperature": 32.5,
                "avg_humidity": 45.2,
                "ndvi_trend": "declining",
                "data_points": 100,
                "min_temperature": 25.0,
                "max_temperature": 40.0,
                "min_humidity": 30.0,
                "max_humidity": 60.0
            },
            "ai_response": "Test response",
            "recommendations": {
                "irrigation": {
                    "priority": "high",
                    "action": "Test action",
                    "reasoning": "Test reasoning"
                }
            },
            "confidence_score": 0.87,
            "created_at": "2026-05-03T14:30:00Z"
        }
        
        recommendation = ai_service._map_to_recommendation(rec_data)
        
        assert isinstance(recommendation, AIRecommendation)
        assert recommendation.device_id == "test_device"
        assert recommendation.confidence_score == 0.87
        assert recommendation.recommendations.irrigation is not None


class TestAIAnalysisRequestValidation:
    """Test AI analysis request validation"""
    
    def test_valid_analysis_request(self):
        """Test valid analysis request"""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.COMPREHENSIVE,
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow()
        )
        
        assert request.analysis_type == AnalysisType.COMPREHENSIVE
        assert request.start_date is not None
        assert request.end_date is not None
    
    def test_invalid_date_range(self):
        """Test invalid date range validation"""
        start_date = datetime.utcnow()
        end_date = datetime.utcnow() - timedelta(days=1)  # End before start
        
        with pytest.raises(ValueError, match="End date must be after start date"):
            AIAnalysisRequest(
                start_date=start_date,
                end_date=end_date
            )


if __name__ == "__main__":
    pytest.main([__file__])
