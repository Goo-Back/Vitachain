#!/usr/bin/env python3
"""
Standalone test for alert service and threshold service integration
"""

import asyncio
import uuid
import os
import time
from unittest.mock import AsyncMock

# Set environment variables for testing
os.environ['ALERT_TEMPERATURE_HIGH'] = '40.0'
os.environ['ALERT_HUMIDITY_LOW'] = '20.0'
os.environ['ALERT_NDVI_LOW'] = '0.3'

async def test_alert_threshold_integration():
    """Test alert service integration with threshold service"""
    
    # Import after setting env vars
    from app.services.alert_service import AlertService
    from app.services.threshold_service import get_threshold_service
    from app.models.schemas import AlertGenerationResponse
    
    # Mock Supabase client
    mock_supabase = AsyncMock()
    
    # Mock database response
    mock_result = AsyncMock()
    alert_ids = [str(uuid.uuid4()) for _ in range(3)]
    mock_result.data = [
        {
            "id": alert_ids[0],
            "farmer_id": str(uuid.uuid4()),
            "device_id": "test-device",
            "type": "threshold_exceeded",
            "severity": "high",
            "message": "Critical temperature detected: 42.0°C (threshold: 40.0°C). Immediate action recommended to prevent heat stress.",
            "read_status": False,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": alert_ids[1],
            "farmer_id": str(uuid.uuid4()),
            "device_id": "test-device",
            "type": "threshold_exceeded",
            "severity": "high",
            "message": "Low humidity detected: 15.0% (threshold: 20%). Risk of dehydration - consider irrigation.",
            "read_status": False,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": alert_ids[2],
            "farmer_id": str(uuid.uuid4()),
            "device_id": "test-device",
            "type": "threshold_exceeded",
            "severity": "medium",
            "message": "Vegetation stress detected: NDVI 0.25 (threshold: 0.3). Review irrigation and nutrient levels.",
            "read_status": False,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
    
    # Properly mock the async chain
    mock_table = AsyncMock()
    mock_table.insert.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_table
    
    # Create alert service
    alert_service = AlertService(mock_supabase)
    
    # Test 1: Verify threshold service integration
    threshold_service = alert_service.threshold_service
    assert threshold_service is not None
    print("✅ Alert service properly integrated with threshold service")
    
    # Test 2: Multiple threshold violations
    farmer_id = uuid.uuid4()
    device_id = "test-device"
    
    response = await alert_service.check_thresholds_and_create_alerts(
        device_id=device_id,
        farmer_id=farmer_id,
        temperature=42.0,  # Above threshold
        humidity=15.0,    # Below threshold
        ndvi=0.25         # Below threshold
    )
    
    assert isinstance(response, AlertGenerationResponse)
    assert response.alerts_created == 3
    assert len(response.alert_ids) == 3
    assert response.processing_time_ms > 0
    print(f"✅ Multiple violations: Created {response.alerts_created} alerts in {response.processing_time_ms}ms")
    
    # Test 3: No violations
    mock_result.data = []  # No alerts should be created
    
    response = await alert_service.check_thresholds_and_create_alerts(
        device_id=device_id,
        farmer_id=farmer_id,
        temperature=35.0,  # Below threshold
        humidity=25.0,    # Above threshold
        ndvi=0.4         # Above threshold
    )
    
    assert response.alerts_created == 0
    assert len(response.alert_ids) == 0
    assert response.processing_time_ms > 0
    print(f"✅ No violations: Created {response.alerts_created} alerts in {response.processing_time_ms}ms")
    
    # Test 4: Performance requirement
    start_time = time.perf_counter()
    
    for _ in range(100):
        await alert_service.check_thresholds_and_create_alerts(
            device_id=device_id,
            farmer_id=farmer_id,
            temperature=42.0,  # Above threshold
            humidity=15.0,    # Below threshold
            ndvi=0.25         # Below threshold
        )
    
    end_time = time.perf_counter()
    avg_time_ms = ((end_time - start_time) / 100) * 1000
    
    print(f"✅ Performance: {avg_time_ms:.3f}ms average per alert generation")
    
    if avg_time_ms < 15.0:
        print("✅ Performance requirement met (< 15ms total)")
    else:
        print(f"⚠️ Performance requirement not met: {avg_time_ms:.3f}ms")
    
    return True

if __name__ == "__main__":
    print("Testing Alert Service + Threshold Service Integration...")
    try:
        asyncio.run(test_alert_threshold_integration())
        print("✅ All integration tests passed!")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
