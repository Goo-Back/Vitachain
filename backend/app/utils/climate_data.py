"""
Climate Data Utilities for Moroccan Agriculture
Provides regional context for AI agronomic recommendations
"""

from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List


class MoroccanClimateContext:
    """Moroccan agricultural climate context provider"""
    
    def __init__(self):
        self.regions = self._initialize_regions()
        self.crop_calendar = self._initialize_crop_calendar()
        self.climate_zones = self._initialize_climate_zones()
    
    def get_context_for_location(self, lat: float, lng: float) -> Dict[str, Any]:
        """
        Get agricultural context for a specific location in Morocco
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            
        Returns:
            Dictionary with regional agricultural context
        """
        region = self._determine_region(lat, lng)
        climate_zone = self._determine_climate_zone(lat, lng)
        current_season = self._get_current_season()
        
        context = {
            "region": region["name"],
            "climate_zone": climate_zone["name"],
            "current_season": current_season,
            "common_crops": region["common_crops"],
            "seasonal_challenges": climate_zone["seasonal_challenges"],
            "water_scarcity_considerations": climate_zone["water_considerations"],
            "soil_types": region["soil_types"],
            "typical_irrigation_methods": region["irrigation_methods"],
            "frost_risk": self._get_frost_risk(lat, current_season),
            "heat_stress_periods": climate_zone["heat_stress_periods"],
            "rainfall_pattern": climate_zone["rainfall_pattern"],
            "growing_season_length": climate_zone["growing_season_days"]
        }
        
        return context
    
    def get_crop_recommendations(self, lat: float, lng: float, season: str) -> List[Dict[str, Any]]:
        """
        Get crop recommendations for location and season
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            season: Current season
            
        Returns:
            List of recommended crops with planting considerations
        """
        region = self._determine_region(lat, lng)
        season_crops = self.crop_calendar.get(season, [])
        
        recommendations = []
        for crop in season_crops:
            if crop["name"] in region["common_crops"]:
                recommendations.append({
                    "name": crop["name"],
                    "suitability": "high",
                    "planting_considerations": crop["planting_considerations"],
                    "water_needs": crop["water_needs"],
                    "growth_period_days": crop["growth_period_days"]
                })
        
        return recommendations
    
    def get_irrigation_recommendations(self, lat: float, lng: float, current_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get irrigation recommendations based on location and current conditions
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            current_conditions: Current sensor data (temperature, humidity, etc.)
            
        Returns:
            Irrigation recommendations and considerations
        """
        climate_zone = self._determine_climate_zone(lat, lng)
        region = self._determine_region(lat, lng)
        
        temperature = current_conditions.get("temperature", 25)
        humidity = current_conditions.get("humidity", 50)
        
        recommendations = {
            "optimal_method": region["irrigation_methods"][0],  # Most efficient method
            "frequency_adjustment": self._calculate_irrigation_frequency(temperature, humidity),
            "water_conservation_priority": climate_zone["water_considerations"]["priority"],
            "evapotranspiration_factor": self._calculate_et_factor(temperature, humidity),
            "soil_moisture_target": region["soil_moisture_target"],
            "irrigation_timing": self._get_optimal_irrigation_timing(climate_zone["name"])
        }
        
        return recommendations
    
    def _initialize_regions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize Moroccan agricultural regions"""
        return {
            "north": {
                "name": "Northern Morocco",
                "lat_range": (34.0, 36.0),
                "lng_range": (-6.0, -2.0),
                "common_crops": ["citrus", "strawberries", "vegetables", "olives", "legumes"],
                "soil_types": ["clay", "sandy loam", "alluvial"],
                "irrigation_methods": ["drip", "sprinkler", "flood"],
                "soil_moisture_target": "60-70%"
            },
            "central": {
                "name": "Central Morocco",
                "lat_range": (32.0, 34.0),
                "lng_range": (-8.0, -5.0),
                "common_crops": ["cereals", "olives", "almonds", "vegetables", "legumes"],
                "soil_types": ["clay", "sandy loam", "calcareous"],
                "irrigation_methods": ["drip", "sprinkler", "center_pivot"],
                "soil_moisture_target": "55-65%"
            },
            "south": {
                "name": "Southern Morocco",
                "lat_range": (28.0, 32.0),
                "lng_range": (-10.0, -7.0),
                "common_crops": ["dates", "argan", "drought_tolerant_vegetables", "melons"],
                "soil_types": ["sandy", "loamy_sand", "calcareous"],
                "irrigation_methods": ["drip", "flood", "subsurface"],
                "soil_moisture_target": "45-55%"
            },
            "east": {
                "name": "Eastern Morocco",
                "lat_range": (32.0, 35.0),
                "lng_range": (-3.0, -1.0),
                "common_crops": ["cereals", "olives", "almonds", "figs"],
                "soil_types": ["clay", "sandy_clay", "stony"],
                "irrigation_methods": ["drip", "sprinkler", "flood"],
                "soil_moisture_target": "50-60%"
            }
        }
    
    def _initialize_climate_zones(self) -> Dict[str, Dict[str, Any]]:
        """Initialize Moroccan climate zones"""
        return {
            "mediterranean": {
                "name": "Mediterranean",
                "lat_range": (34.0, 36.0),
                "seasonal_challenges": ["high_humidity", "frost_risk", "coastal_winds", "pest_pressure"],
                "water_considerations": {
                    "priority": "medium",
                    "description": "Moderate water availability, conservation recommended"
                },
                "heat_stress_periods": ["july", "august"],
                "rainfall_pattern": "winter_dominant",
                "growing_season_days": 280
            },
            "continental": {
                "name": "Continental",
                "lat_range": (32.0, 34.0),
                "seasonal_challenges": ["temperature_extremes", "limited_rainfall", "soil_degradation"],
                "water_considerations": {
                    "priority": "high",
                    "description": "Limited water availability, efficient irrigation essential"
                },
                "heat_stress_periods": ["june", "july", "august"],
                "rainfall_pattern": "variable",
                "growing_season_days": 250
            },
            "arid": {
                "name": "Arid/Semi-arid",
                "lat_range": (28.0, 32.0),
                "seasonal_challenges": ["extreme_heat", "water_scarcity", "desertification", "high_evaporation"],
                "water_considerations": {
                    "priority": "critical",
                    "description": "Critical water conservation, drip irrigation essential"
                },
                "heat_stress_periods": ["may", "june", "july", "august", "september"],
                "rainfall_pattern": "minimal",
                "growing_season_days": 200
            },
            "atlantic": {
                "name": "Atlantic",
                "lat_range": (33.0, 35.0),
                "seasonal_challenges": ["coastal_fog", "salt_spray", "moderate_humidity", "wind_exposure"],
                "water_considerations": {
                    "priority": "medium",
                    "description": "Moderate water with oceanic influence"
                },
                "heat_stress_periods": ["july", "august"],
                "rainfall_pattern": "winter_dominant",
                "growing_season_days": 270
            }
        }
    
    def _initialize_crop_calendar(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize crop planting calendar for Morocco"""
        return {
            "spring": [
                {
                    "name": "tomatoes",
                    "planting_considerations": "Start indoors, transplant after frost risk",
                    "water_needs": "high",
                    "growth_period_days": 90
                },
                {
                    "name": "peppers",
                    "planting_considerations": "Warm soil required, protect from wind",
                    "water_needs": "moderate",
                    "growth_period_days": 85
                },
                {
                    "name": "beans",
                    "planting_considerations": "Direct sow after soil warms",
                    "water_needs": "moderate",
                    "growth_period_days": 60
                }
            ],
            "summer": [
                {
                    "name": "melons",
                    "planting_considerations": "Heat-loving, requires full sun",
                    "water_needs": "high",
                    "growth_period_days": 80
                },
                {
                    "name": "squash",
                    "planting_considerations": "Rapid growth, regular harvesting",
                    "water_needs": "high",
                    "growth_period_days": 70
                },
                {
                    "name": "corn",
                    "planting_considerations": "Plant in blocks for pollination",
                    "water_needs": "high",
                    "growth_period_days": 90
                }
            ],
            "autumn": [
                {
                    "name": "lettuce",
                    "planting_considerations": "Cool weather crop, quick growth",
                    "water_needs": "moderate",
                    "growth_period_days": 45
                },
                {
                    "name": "spinach",
                    "planting_considerations": "Cold tolerant, successive planting",
                    "water_needs": "moderate",
                    "growth_period_days": 40
                },
                {
                    "name": "carrots",
                    "planting_considerations": "Deep soil required, thin seedlings",
                    "water_needs": "moderate",
                    "growth_period_days": 75
                }
            ],
            "winter": [
                {
                    "name": "fava_beans",
                    "planting_considerations": "Cold tolerant, nitrogen fixing",
                    "water_needs": "low",
                    "growth_period_days": 120
                },
                {
                    "name": "peas",
                    "planting_considerations": "Cool season, support required",
                    "water_needs": "moderate",
                    "growth_period_days": 70
                },
                {
                    "name": "broccoli",
                    "planting_considerations": "Cool weather, uniform watering",
                    "water_needs": "moderate",
                    "growth_period_days": 60
                }
            ]
        }
    
    def _determine_region(self, lat: float, lng: float) -> Dict[str, Any]:
        """Determine agricultural region based on coordinates"""
        for region_key, region_data in self.regions.items():
            lat_min, lat_max = region_data["lat_range"]
            lng_min, lng_max = region_data["lng_range"]
            
            if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
                return region_data
        
        # Default to central region if no match
        return self.regions["central"]
    
    def _determine_climate_zone(self, lat: float, lng: float) -> Dict[str, Any]:
        """Determine climate zone based on coordinates"""
        for zone_key, zone_data in self.climate_zones.items():
            lat_min, lat_max = zone_data["lat_range"]
            
            if lat_min <= lat <= lat_max:
                return zone_data
        
        # Default to continental zone if no match
        return self.climate_zones["continental"]
    
    def _get_current_season(self) -> str:
        """Get current agricultural season in Morocco"""
        month = datetime.utcnow().month
        
        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "autumn"
        else:
            return "winter"
    
    def _get_frost_risk(self, lat: float, season: str) -> Dict[str, Any]:
        """Get frost risk assessment"""
        # Northern regions have higher frost risk
        if lat > 34.0:
            if season == "winter":
                return {"risk": "high", "period": "december_february"}
            elif season == "autumn":
                return {"risk": "medium", "period": "november_december"}
            elif season == "spring":
                return {"risk": "medium", "period": "february_march"}
        
        return {"risk": "low", "period": "none"}
    
    def _calculate_irrigation_frequency(self, temperature: float, humidity: float) -> str:
        """Calculate irrigation frequency adjustment"""
        if temperature > 35 and humidity < 30:
            return "increase_frequency"
        elif temperature < 20 and humidity > 70:
            return "decrease_frequency"
        else:
            return "normal"
    
    def _calculate_et_factor(self, temperature: float, humidity: float) -> float:
        """Calculate evapotranspiration factor"""
        # Simplified ET calculation based on temperature and humidity
        base_et = 0.5
        temp_factor = (temperature - 20) * 0.02  # Increase with temperature
        humidity_factor = (70 - humidity) * 0.01  # Increase with lower humidity
        
        et_factor = base_et + temp_factor + humidity_factor
        return max(0.1, min(1.0, et_factor))
    
    def _get_optimal_irrigation_timing(self, climate_zone: str) -> Dict[str, str]:
        """Get optimal irrigation timing based on climate zone"""
        timing_recommendations = {
            "mediterranean": {
                "time": "early_morning",
                "reason": "Reduces evaporation, allows foliage to dry"
            },
            "continental": {
                "time": "early_morning_or_late_evening",
                "reason": "Avoids heat stress, maximizes absorption"
            },
            "arid": {
                "time": "late_evening",
                "reason": "Minimizes evaporation losses"
            },
            "atlantic": {
                "time": "early_morning",
                "reason": "Works with coastal humidity patterns"
            }
        }
        
        return timing_recommendations.get(climate_zone, timing_recommendations["continental"])


# Global instance for use across the application
moroccan_climate = MoroccanClimateContext()
