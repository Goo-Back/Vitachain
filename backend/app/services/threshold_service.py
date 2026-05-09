"""
Threshold Service for KATARA alert system
Handles threshold checking logic and configuration management
"""

import os
import math
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.logging import get_logger
from app.models.schemas import (
    ThresholdConfig, ThresholdViolation, AlertSeverity, MetricType
)

logger = get_logger(__name__)

# Default threshold values
DEFAULT_THRESHOLDS = ThresholdConfig()


class ThresholdService:
    """Service for handling threshold checking and configuration."""
    
    def __init__(self):
        """Initialize threshold service with configuration."""
        self.logger = get_logger(f"{__name__}.ThresholdService")
        self.thresholds = self._load_threshold_config()
    
    def _load_threshold_config(self) -> ThresholdConfig:
        """Load threshold configuration from environment variables."""
        try:
            temp_high = os.getenv("ALERT_TEMPERATURE_HIGH")
            humidity_low = os.getenv("ALERT_HUMIDITY_LOW")
            ndvi_low = os.getenv("ALERT_NDVI_LOW")
            
            return ThresholdConfig(
                temperature_high=float(temp_high.strip()) if temp_high else DEFAULT_THRESHOLDS.temperature_high,
                humidity_low=float(humidity_low.strip()) if humidity_low else DEFAULT_THRESHOLDS.humidity_low,
                ndvi_low=float(ndvi_low.strip()) if ndvi_low else DEFAULT_THRESHOLDS.ndvi_low
            )
        except (ValueError, TypeError):
            # Fall back to defaults if environment variables are invalid
            self.logger.warning("invalid_threshold_env_vars", 
                              temp_high=temp_high, 
                              humidity_low=humidity_low, 
                              ndvi_low=ndvi_low)
            return DEFAULT_THRESHOLDS
    
    def check_temperature_threshold(self, temperature: float) -> Optional[ThresholdViolation]:
        """
        Check if temperature exceeds high threshold.
        
        Args:
            temperature: Temperature reading in Celsius
            
        Returns:
            Threshold violation info or None if within limits
        """
        # Handle invalid values
        if temperature is None or not isinstance(temperature, (int, float)) or math.isnan(temperature) or math.isinf(temperature):
            return None
            
        if temperature > self.thresholds.temperature_high:
            return ThresholdViolation(
                metric=MetricType.TEMPERATURE,
                value=temperature,
                threshold=self.thresholds.temperature_high,
                severity=AlertSeverity.HIGH,
                operator=">",
                violation_amount=temperature - self.thresholds.temperature_high
            )
        return None
    
    def check_humidity_threshold(self, humidity: float) -> Optional[ThresholdViolation]:
        """
        Check if humidity falls below low threshold.
        
        Args:
            humidity: Humidity reading in percentage
            
        Returns:
            Threshold violation info or None if within limits
        """
        # Handle invalid values
        if humidity is None or not isinstance(humidity, (int, float)) or math.isnan(humidity) or math.isinf(humidity):
            return None
            
        if humidity < self.thresholds.humidity_low:
            return ThresholdViolation(
                metric=MetricType.HUMIDITY,
                value=humidity,
                threshold=self.thresholds.humidity_low,
                severity=AlertSeverity.HIGH,
                operator="<",
                violation_amount=self.thresholds.humidity_low - humidity
            )
        return None
    
    def check_ndvi_threshold(self, ndvi: float) -> Optional[ThresholdViolation]:
        """
        Check if NDVI falls below low threshold.
        
        Args:
            ndvi: NDVI reading
            
        Returns:
            Threshold violation info or None if within limits
        """
        # Handle invalid values or None
        if ndvi is None or not isinstance(ndvi, (int, float)) or math.isnan(ndvi) or math.isinf(ndvi):
            return None
            
        if ndvi < self.thresholds.ndvi_low:
            return ThresholdViolation(
                metric=MetricType.NDVI,
                value=ndvi,
                threshold=self.thresholds.ndvi_low,
                severity=AlertSeverity.MEDIUM,
                operator="<",
                violation_amount=self.thresholds.ndvi_low - ndvi
            )
        return None
    
    def check_all_thresholds(
        self, 
        temperature: float, 
        humidity: float, 
        ndvi: Optional[float] = None
    ) -> List[ThresholdViolation]:
        """
        Check all thresholds against provided readings.
        
        Args:
            temperature: Temperature reading in Celsius
            humidity: Humidity reading in percentage
            ndvi: Optional NDVI reading
            
        Returns:
            List of threshold violations
        """
        violations = []
        
        # Check temperature
        temp_violation = self.check_temperature_threshold(temperature)
        if temp_violation:
            violations.append(temp_violation)
        
        # Check humidity
        humidity_violation = self.check_humidity_threshold(humidity)
        if humidity_violation:
            violations.append(humidity_violation)
        
        # Check NDVI if provided
        if ndvi is not None:
            ndvi_violation = self.check_ndvi_threshold(ndvi)
            if ndvi_violation:
                violations.append(ndvi_violation)
        
        return violations
    
    def get_threshold_config(self) -> ThresholdConfig:
        """Get current threshold configuration."""
        return self.thresholds
    
    def update_threshold_config(self, new_config: ThresholdConfig) -> ThresholdConfig:
        """
        Update threshold configuration.
        
        Args:
            new_config: New threshold configuration
            
        Returns:
            Updated threshold configuration
        """
        # Validate thresholds
        if not (-10 <= new_config.temperature_high <= 60):
            raise ValueError("Temperature threshold must be between -10°C and 60°C")
        
        if not (0 <= new_config.humidity_low <= 100):
            raise ValueError("Humidity threshold must be between 0% and 100%")
        
        if not (-1 <= new_config.ndvi_low <= 1):
            raise ValueError("NDVI threshold must be between -1 and 1")
        
        self.thresholds = new_config
        self.logger.info("threshold_config_updated", new_config=new_config.dict())
        
        return self.thresholds
    
    def validate_metric_value(self, metric: MetricType, value: float) -> bool:
        """
        Validate if a metric value is within acceptable ranges.
        
        Args:
            metric: Type of metric
            value: Metric value to validate
            
        Returns:
            True if value is valid, False otherwise
        """
        if not isinstance(metric, MetricType):
            raise ValueError(f"Invalid metric type: {metric}")
            
        if metric == MetricType.TEMPERATURE:
            return -10 <= value <= 60
        elif metric == MetricType.HUMIDITY:
            return 0 <= value <= 100
        elif metric == MetricType.NDVI:
            return -1 <= value <= 1
        else:
            raise ValueError(f"Unknown metric type: {metric}")
    
    def get_metric_health_status(self, metric: MetricType, value: float) -> str:
        """
        Get health status for a metric value.
        
        Args:
            metric: Type of metric
            value: Metric value
            
        Returns:
            Health status string
        """
        if not self.validate_metric_value(metric, value):
            return "invalid"
        
        violation = None
        if metric == MetricType.TEMPERATURE:
            violation = self.check_temperature_threshold(value)
        elif metric == MetricType.HUMIDITY:
            violation = self.check_humidity_threshold(value)
        elif metric == MetricType.NDVI:
            violation = self.check_ndvi_threshold(value)
        
        if violation:
            return f"alert_{violation.severity.value}"
        
        return "healthy"
    
    def get_threshold_summary(self) -> Dict[str, Any]:
        """
        Get summary of current threshold configuration.
        
        Returns:
            Dictionary with threshold summary
        """
        return {
            "temperature": {
                "high_threshold": self.thresholds.temperature_high,
                "unit": "°C",
                "operator": ">"
            },
            "humidity": {
                "low_threshold": self.thresholds.humidity_low,
                "unit": "%",
                "operator": "<"
            },
            "ndvi": {
                "low_threshold": self.thresholds.ndvi_low,
                "unit": "NDVI",
                "operator": "<"
            },
            "last_updated": datetime.utcnow().isoformat()
        }


# Factory function for dependency injection
def get_threshold_service() -> ThresholdService:
    """Create threshold service instance."""
    return ThresholdService()
