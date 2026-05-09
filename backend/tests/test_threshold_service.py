"""
Tests for Threshold Service
Tests threshold validation logic and configuration management
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from app.services.threshold_service import ThresholdService, ThresholdConfig, ThresholdViolation
from app.models.schemas import MetricType, AlertSeverity


class TestThresholdConfig:
    """Test threshold configuration management"""
    
    def test_default_threshold_values(self):
        """Test default threshold values"""
        config = ThresholdConfig()
        
        assert config.temperature_high == 40.0
        assert config.humidity_low == 20.0
        assert config.ndvi_low == 0.3
    
    @patch.dict(os.environ, {
        'ALERT_TEMPERATURE_HIGH': '45.0',
        'ALERT_HUMIDITY_LOW': '15.0',
        'ALERT_NDVI_LOW': '0.25'
    })
    def test_environment_variable_configuration(self):
        """Test loading thresholds from environment variables"""
        service = ThresholdService()
        config = service.get_threshold_config()
        
        assert config.temperature_high == 45.0
        assert config.humidity_low == 15.0
        assert config.ndvi_low == 0.25
    
    @patch.dict(os.environ, {
        'ALERT_TEMPERATURE_HIGH': 'invalid'
    })
    def test_invalid_environment_variable_uses_default(self):
        """Test that invalid environment variables use defaults"""
        config = ThresholdConfig()
        
        # Should fall back to default when invalid value provided
        assert config.temperature_high == 40.0  # Default value


class TestThresholdService:
    """Test threshold validation service"""
    
    def setup_method(self):
        """Setup test threshold service"""
        self.threshold_service = ThresholdService()
    
    def test_temperature_threshold_violation(self):
        """Test temperature threshold violation detection"""
        # Temperature above threshold (40°C)
        violation = self.threshold_service.check_temperature_threshold(42.5)
        
        assert violation is not None
        assert violation.metric == MetricType.TEMPERATURE
        assert violation.value == 42.5
        assert violation.threshold == 40.0
        assert violation.severity == AlertSeverity.HIGH
        assert violation.operator == ">"
        assert violation.violation_amount == 2.5
    
    def test_temperature_threshold_normal(self):
        """Test temperature within normal range"""
        violation = self.threshold_service.check_temperature_threshold(35.0)
        assert violation is None
    
    def test_temperature_threshold_exact_boundary(self):
        """Test temperature exactly at threshold"""
        violation = self.threshold_service.check_temperature_threshold(40.0)
        assert violation is None  # Exactly at threshold should not trigger
    
    def test_humidity_threshold_violation(self):
        """Test humidity threshold violation detection"""
        # Humidity below threshold (20%)
        violation = self.threshold_service.check_humidity_threshold(15.0)
        
        assert violation is not None
        assert violation.metric == MetricType.HUMIDITY
        assert violation.value == 15.0
        assert violation.threshold == 20.0
        assert violation.severity == AlertSeverity.HIGH
        assert violation.operator == "<"
        assert violation.violation_amount == 5.0
    
    def test_humidity_threshold_normal(self):
        """Test humidity within normal range"""
        violation = self.threshold_service.check_humidity_threshold(25.0)
        assert violation is None
    
    def test_humidity_threshold_exact_boundary(self):
        """Test humidity exactly at threshold"""
        violation = self.threshold_service.check_humidity_threshold(20.0)
        assert violation is None  # Exactly at threshold should not trigger
    
    def test_ndvi_threshold_violation(self):
        """Test NDVI threshold violation detection"""
        # NDVI below threshold (0.3)
        violation = self.threshold_service.check_ndvi_threshold(0.25)
        
        assert violation is not None
        assert violation.metric == MetricType.NDVI
        assert violation.value == 0.25
        assert violation.threshold == 0.3
        assert violation.severity == AlertSeverity.MEDIUM
        assert violation.operator == "<"
        assert abs(violation.violation_amount - 0.05) < 1e-10
    
    def test_ndvi_threshold_normal(self):
        """Test NDVI within normal range"""
        violation = self.threshold_service.check_ndvi_threshold(0.4)
        assert violation is None
    
    def test_ndvi_threshold_exact_boundary(self):
        """Test NDVI exactly at threshold"""
        violation = self.threshold_service.check_ndvi_threshold(0.3)
        assert violation is None  # Exactly at threshold should not trigger
    
    def test_ndvi_threshold_none_value(self):
        """Test NDVI with None value (no violation)"""
        violation = self.threshold_service.check_ndvi_threshold(None)
        assert violation is None
    
    def test_check_all_thresholds_multiple_violations(self):
        """Test checking all thresholds with multiple violations"""
        violations = self.threshold_service.check_all_thresholds(
            temperature=42.0,  # Above threshold
            humidity=15.0,      # Below threshold
            ndvi=0.25          # Below threshold
        )
        
        assert len(violations) == 3
        assert any(v.metric == MetricType.TEMPERATURE for v in violations)
        assert any(v.metric == MetricType.HUMIDITY for v in violations)
        assert any(v.metric == MetricType.NDVI for v in violations)
    
    def test_check_all_thresholds_no_violations(self):
        """Test checking all thresholds with no violations"""
        violations = self.threshold_service.check_all_thresholds(
            temperature=35.0,  # Below threshold
            humidity=25.0,      # Above threshold
            ndvi=0.4            # Above threshold
        )
        
        assert len(violations) == 0
    
    def test_check_all_thresholds_partial_violations(self):
        """Test checking all thresholds with some violations"""
        violations = self.threshold_service.check_all_thresholds(
            temperature=42.0,  # Above threshold
            humidity=25.0,      # Above threshold (normal)
            ndvi=0.25          # Below threshold
        )
        
        assert len(violations) == 2
        assert any(v.metric == MetricType.TEMPERATURE for v in violations)
        assert any(v.metric == MetricType.NDVI for v in violations)
        assert not any(v.metric == MetricType.HUMIDITY for v in violations)
    
    def test_validate_metric_value_temperature(self):
        """Test temperature metric validation"""
        # Valid values
        assert self.threshold_service.validate_metric_value(MetricType.TEMPERATURE, 25.0)
        assert self.threshold_service.validate_metric_value(MetricType.TEMPERATURE, -5.0)  # Within range
        
        # Invalid values
        assert not self.threshold_service.validate_metric_value(MetricType.TEMPERATURE, -15.0)  # Too cold
        assert not self.threshold_service.validate_metric_value(MetricType.TEMPERATURE, 65.0)   # Too hot
    
    def test_validate_metric_value_humidity(self):
        """Test humidity metric validation"""
        # Valid values
        assert self.threshold_service.validate_metric_value(MetricType.HUMIDITY, 50.0)
        assert self.threshold_service.validate_metric_value(MetricType.HUMIDITY, 0.0)    # Minimum
        assert self.threshold_service.validate_metric_value(MetricType.HUMIDITY, 100.0)  # Maximum
        
        # Invalid values
        assert not self.threshold_service.validate_metric_value(MetricType.HUMIDITY, -5.0)   # Too low
        assert not self.threshold_service.validate_metric_value(MetricType.HUMIDITY, 105.0)  # Too high
    
    def test_validate_metric_value_ndvi(self):
        """Test NDVI metric validation"""
        # Valid values
        assert self.threshold_service.validate_metric_value(MetricType.NDVI, 0.5)
        assert self.threshold_service.validate_metric_value(MetricType.NDVI, -1.0)   # Minimum
        assert self.threshold_service.validate_metric_value(MetricType.NDVI, 1.0)    # Maximum
        
        # Invalid values
        assert not self.threshold_service.validate_metric_value(MetricType.NDVI, -1.5)  # Too low
        assert not self.threshold_service.validate_metric_value(MetricType.NDVI, 1.5)   # Too high
    
    def test_validate_metric_value_invalid_type(self):
        """Test validation with invalid metric type"""
        with pytest.raises(ValueError):
            self.threshold_service.validate_metric_value("invalid_type", 25.0)
    
    def test_get_threshold_config(self):
        """Test getting threshold configuration"""
        config = self.threshold_service.get_threshold_config()
        
        assert isinstance(config, ThresholdConfig)
        assert hasattr(config, 'temperature_high')
        assert hasattr(config, 'humidity_low')
        assert hasattr(config, 'ndvi_low')
    
    def test_performance_threshold_checking(self):
        """Test that threshold checking meets performance requirements"""
        import time
        
        # Test single threshold check performance
        start_time = time.perf_counter()
        
        for _ in range(1000):
            self.threshold_service.check_temperature_threshold(42.0)
            self.threshold_service.check_humidity_threshold(15.0)
            self.threshold_service.check_ndvi_threshold(0.25)
        
        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / 3000) * 1000
        
        # Should be well under 5ms requirement
        assert avg_time_ms < 1.0, f"Threshold checking too slow: {avg_time_ms:.3f}ms average"
    
    def test_error_handling_in_threshold_checks(self):
        """Test that threshold checks handle errors gracefully"""
        # Test with extreme values that shouldn't cause crashes
        violation = self.threshold_service.check_temperature_threshold(float('inf'))
        assert violation is None  # Should handle gracefully
        
        violation = self.threshold_service.check_humidity_threshold(float('nan'))
        assert violation is None  # Should handle gracefully


class TestThresholdViolation:
    """Test threshold violation data structure"""
    
    def test_threshold_violation_creation(self):
        """Test creating threshold violation objects"""
        violation = ThresholdViolation(
            metric=MetricType.TEMPERATURE,
            value=42.5,
            threshold=40.0,
            severity=AlertSeverity.HIGH,
            operator=">",
            violation_amount=2.5
        )
        
        assert violation.metric == MetricType.TEMPERATURE
        assert violation.value == 42.5
        assert violation.threshold == 40.0
        assert violation.severity == AlertSeverity.HIGH
        assert violation.operator == ">"
        assert violation.violation_amount == 2.5
    
    def test_threshold_violation_repr(self):
        """Test threshold violation string representation"""
        violation = ThresholdViolation(
            metric=MetricType.TEMPERATURE,
            value=42.5,
            threshold=40.0,
            severity=AlertSeverity.HIGH,
            operator=">",
            violation_amount=2.5
        )
        
        repr_str = repr(violation)
        assert "temperature" in repr_str
        assert "42.5" in repr_str
        assert "40.0" in repr_str
        assert "high" in repr_str


if __name__ == "__main__":
    pytest.main([__file__])
