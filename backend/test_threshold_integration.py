#!/usr/bin/env python3
"""
Simple test script to verify threshold service integration
"""

import os
from app.services.threshold_service import get_threshold_service

# Set environment variables for testing
os.environ['ALERT_TEMPERATURE_HIGH'] = '40.0'
os.environ['ALERT_HUMIDITY_LOW'] = '20.0'
os.environ['ALERT_NDVI_LOW'] = '0.3'

def test_threshold_service_integration():
    """Test threshold service functionality"""
    
    # Get threshold service
    threshold_service = get_threshold_service()
    
    # Test configuration loading
    config = threshold_service.get_threshold_config()
    assert config.temperature_high == 40.0
    assert config.humidity_low == 20.0
    assert config.ndvi_low == 0.3
    print("✅ Environment variable configuration working")
    
    # Test threshold violations
    violations = threshold_service.check_all_thresholds(
        temperature=42.0,  # Above threshold
        humidity=15.0,    # Below threshold
        ndvi=0.25         # Below threshold
    )
    
    assert len(violations) == 3
    print("✅ Multiple threshold violations detected correctly")
    
    # Test no violations
    violations = threshold_service.check_all_thresholds(
        temperature=35.0,  # Below threshold
        humidity=25.0,    # Above threshold
        ndvi=0.4         # Above threshold
    )
    
    assert len(violations) == 0
    print("✅ Normal values correctly identified (no violations)")
    
    # Test individual threshold checks
    temp_violation = threshold_service.check_temperature_threshold(42.0)
    assert temp_violation is not None
    assert temp_violation.metric.value == "temperature"
    assert temp_violation.value == 42.0
    assert temp_violation.threshold == 40.0
    assert temp_violation.severity.value == "high"
    print("✅ Temperature threshold checking working")
    
    humidity_violation = threshold_service.check_humidity_threshold(15.0)
    assert humidity_violation is not None
    assert humidity_violation.metric.value == "humidity"
    assert humidity_violation.value == 15.0
    assert humidity_violation.threshold == 20.0
    assert humidity_violation.severity.value == "high"
    print("✅ Humidity threshold checking working")
    
    ndvi_violation = threshold_service.check_ndvi_threshold(0.25)
    assert ndvi_violation is not None
    assert ndvi_violation.metric.value == "ndvi"
    assert ndvi_violation.value == 0.25
    assert ndvi_violation.threshold == 0.3
    assert ndvi_violation.severity.value == "medium"
    print("✅ NDVI threshold checking working")
    
    # Test performance
    import time
    start_time = time.perf_counter()
    
    for _ in range(1000):
        threshold_service.check_all_thresholds(42.0, 15.0, 0.25)
    
    end_time = time.perf_counter()
    avg_time_ms = ((end_time - start_time) / 1000) * 1000
    
    print(f"✅ Performance: {avg_time_ms:.3f}ms average per check")
    
    if avg_time_ms < 1.0:
        print("✅ Performance requirement met (< 1ms)")
    else:
        print(f"⚠️ Performance requirement not met: {avg_time_ms:.3f}ms")
    
    return True

if __name__ == "__main__":
    print("Testing Threshold Service Integration...")
    try:
        test_threshold_service_integration()
        print("✅ All threshold service tests passed!")
    except Exception as e:
        print(f"❌ Threshold service test failed: {e}")
        import traceback
        traceback.print_exc()
