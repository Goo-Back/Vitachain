#!/usr/bin/env python3
"""
Simple test script to verify alert service integration with threshold service
"""

import asyncio
import uuid
import os
from unittest.mock import AsyncMock

# Set environment variables for testing
os.environ['ALERT_TEMPERATURE_HIGH'] = '40.0'
os.environ['ALERT_HUMIDITY_LOW'] = '20.0'
os.environ['ALERT_NDVI_LOW'] = '0.3'

async def test_alert_service_integration():
    """Test that alert service uses threshold service correctly"""
    
    # Import after setting env vars
    from app.services.alert_service import AlertService
    from app.services.threshold_service import get_threshold_service
    
    # Mock Supabase client
    mock_supabase = AsyncMock()
    
    # Mock database response
    mock_result = AsyncMock()
    mock_result.data = [{
        "id": str(uuid.uuid4()),
        "farmer_id": str(uuid.uuid4()),
        "device_id": "test-device",
        "type": "threshold_exceeded",
        "severity": "high",
        "message": "Test alert",
        "read_status": False,
        "created_at": "2024-01-01T00:00:00Z"
    }]
    
    # Properly mock the async chain
    mock_table = AsyncMock()
    mock_table.insert.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_table
    
    # Create alert service
    alert_service = AlertService(mock_supabase)
    
    # Test that threshold service is properly integrated
    threshold_service = alert_service.threshold_service
    assert threshold_service is not None
    
    # Test threshold checking
    violations = threshold_service.check_all_thresholds(
        temperature=42.0,  # Above threshold
        humidity=15.0,    # Below threshold
        ndvi=0.25         # Below threshold
    )
    
    assert len(violations) == 3
    print("✅ Threshold service integration working correctly")
    
    # Test alert generation
    farmer_id = uuid.uuid4()
    device_id = "test-device"
    
    response = await alert_service.check_thresholds_and_create_alerts(
        device_id=device_id,
        farmer_id=farmer_id,
        temperature=42.0,  # Above threshold
        humidity=15.0,    # Below threshold
        ndvi=0.25         # Below threshold
    )
    
    assert response.alerts_created == 3
    assert len(response.alert_ids) == 3
    assert response.processing_time_ms > 0
    
    print("✅ Alert service integration working correctly")
    print(f"✅ Created {response.alerts_created} alerts in {response.processing_time_ms}ms")
    
    # Test performance requirement
    if response.processing_time_ms < 15:
        print("✅ Performance requirement met (< 15ms)")
    else:
        print(f"⚠️ Performance requirement not met: {response.processing_time_ms}ms")
    
    return True

if __name__ == "__main__":
    print("Testing Alert Service Integration...")
    try:
        asyncio.run(test_alert_service_integration())
        print("✅ All integration tests passed!")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
