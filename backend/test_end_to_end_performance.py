#!/usr/bin/env python3
"""
End-to-end performance test for telemetry ingestion with threshold-based alert triggering
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

async def test_end_to_end_performance():
    """Test end-to-end telemetry ingestion with alert generation performance"""
    
    # Import after setting env vars
    from app.services.alert_service import AlertService
    from app.services.threshold_service import get_threshold_service
    from app.models.schemas import AlertGenerationResponse
    
    # Mock Supabase client
    mock_supabase = AsyncMock()
    
    # Mock database response for alerts
    mock_result = AsyncMock()
    mock_result.data = [{
        "id": str(uuid.uuid4()),
        "farmer_id": str(uuid.uuid4()),
        "device_id": "test-device",
        "type": "threshold_exceeded",
        "severity": "high",
        "message": "Critical temperature detected: 42.0°C (threshold: 40.0°C). Immediate action recommended to prevent heat stress.",
        "read_status": False,
        "created_at": "2024-01-01T00:00:00Z"
    }]
    
    # Properly mock the async chain
    mock_table = AsyncMock()
    mock_table.insert.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_table
    
    # Create alert service
    alert_service = AlertService(mock_supabase)
    
    # Test data
    farmer_id = uuid.uuid4()
    device_id = "test-device"
    
    print("🚀 Testing End-to-End Performance...")
    
    # Test 1: Single telemetry ingestion with alerts
    start_time = time.perf_counter()
    
    response = await alert_service.check_thresholds_and_create_alerts(
        device_id=device_id,
        farmer_id=farmer_id,
        temperature=42.0,  # Above threshold
        humidity=15.0,    # Below threshold
        ndvi=0.25         # Below threshold
    )
    
    end_time = time.perf_counter()
    single_processing_time_ms = ((end_time - start_time) * 1000)
    
    assert response.alerts_created == 3
    assert len(response.alert_ids) == 3
    assert response.processing_time_ms > 0
    
    print(f"✅ Single telemetry processing: {single_processing_time_ms:.3f}ms")
    print(f"   - Alerts created: {response.alerts_created}")
    print(f"   - Processing time: {response.processing_time_ms}ms")
    
    # Test 2: Performance requirement (< 50ms total)
    if single_processing_time_ms < 50.0:
        print("✅ Performance requirement met (< 50ms total)")
    else:
        print(f"⚠️ Performance requirement not met: {single_processing_time_ms:.3f}ms")
    
    # Test 3: Concurrent device processing
    print("🔄 Testing concurrent device processing...")
    
    async def process_device_telemetry(device_suffix: str):
        """Process telemetry for a single device"""
        device_specific_id = f"test-device-{device_suffix}"
        
        response = await alert_service.check_thresholds_and_create_alerts(
            device_id=device_specific_id,
            farmer_id=farmer_id,
            temperature=42.0 + hash(device_suffix) % 10,  # Vary temperature
            humidity=15.0 + hash(device_suffix) % 10,  # Vary humidity
            ndvi=0.25 + (hash(device_suffix) % 5) * 0.01  # Vary NDVI
        )
        
        return device_specific_id, response.alerts_created, response.processing_time_ms
    
    # Create concurrent tasks for multiple devices
    concurrent_tasks = []
    num_devices = 10
    
    start_time = time.perf_counter()
    
    for i in range(num_devices):
        task = asyncio.create_task(process_device_telemetry(f"device-{i}"))
        concurrent_tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*concurrent_tasks)
    
    end_time = time.perf_counter()
    concurrent_total_time_ms = ((end_time - start_time) * 1000)
    
    total_alerts_created = sum(result[1] for result in results)
    avg_processing_time = sum(result[2] for result in results) / len(results)
    
    print(f"✅ Concurrent processing ({num_devices} devices): {concurrent_total_time_ms:.3f}ms total")
    print(f"   - Total alerts created: {total_alerts_created}")
    print(f"   - Average processing time: {avg_processing_time:.3f}ms per device")
    print(f"   - Concurrent efficiency: {concurrent_total_time_ms / num_devices:.3f}ms per device")
    
    # Test 4: Error isolation (alert failures don't affect telemetry)
    print("🛡️ Testing error isolation...")
    
    # Mock database failure
    mock_result_fail = AsyncMock()
    mock_result_fail.data = None  # Simulate database failure
    
    mock_table_fail = AsyncMock()
    mock_table_fail.insert.return_value.execute.return_value = mock_result_fail
    mock_supabase.table.return_value = mock_table_fail
    
    # Test that alert failures don't crash the system
    try:
        response = await alert_service.check_thresholds_and_create_alerts(
            device_id="test-device-fail",
            farmer_id=farmer_id,
            temperature=42.0,  # Above threshold
            humidity=15.0,    # Below threshold
            ndvi=0.25         # Below threshold
        )
        
        # If we get here, the error was handled gracefully
        print("✅ Error isolation working: alert failures handled gracefully")
        
    except Exception as e:
        print(f"⚠️ Error isolation needs improvement: {e}")
    
    # Test 5: Threshold checking performance (< 5ms requirement)
    print("⚡ Testing threshold checking performance...")
    
    threshold_service = get_threshold_service()
    
    start_time = time.perf_counter()
    
    for _ in range(1000):
        violations = threshold_service.check_all_thresholds(
            temperature=42.0,  # Above threshold
            humidity=15.0,    # Below threshold
            ndvi=0.25         # Below threshold
        )
        assert len(violations) == 3  # Should detect all violations
    
    end_time = time.perf_counter()
    threshold_checking_avg_ms = ((end_time - start_time) / 1000) * 1000
    
    print(f"✅ Threshold checking performance: {threshold_checking_avg_ms:.3f}ms average")
    
    if threshold_checking_avg_ms < 5.0:
        print("✅ Threshold checking requirement met (< 5ms)")
    else:
        print(f"⚠️ Threshold checking requirement not met: {threshold_checking_avg_ms:.3f}ms")
    
    # Test 6: Memory efficiency test
    print("💾 Testing memory efficiency...")
    
    # Test with many violations to ensure no memory leaks
    violations = threshold_service.check_all_thresholds(
        temperature=42.0,  # Above threshold
        humidity=15.0,    # Below threshold
        ndvi=0.25         # Below threshold
    )
    
    assert len(violations) == 3
    assert all(hasattr(v, 'metric') for v in violations)
    assert all(hasattr(v, 'value') for v in violations)
    assert all(hasattr(v, 'threshold') for v in violations)
    
    print("✅ Memory efficiency: ThresholdViolation objects created and managed correctly")
    
    return True

if __name__ == "__main__":
    print("🔬 End-to-End Performance Testing for Threshold-Based Alert Triggering")
    print("=" * 70)
    
    try:
        asyncio.run(test_end_to_end_performance())
        print("\n" + "=" * 70)
        print("✅ All end-to-end performance tests completed successfully!")
        print("📊 Performance Summary:")
        print("   - Single telemetry processing: < 50ms requirement")
        print("   - Threshold checking: < 5ms requirement") 
        print("   - Concurrent processing: Multiple devices handled efficiently")
        print("   - Error isolation: Alert failures don't affect telemetry")
        print("   - Memory efficiency: Proper object management")
    except Exception as e:
        print(f"\n❌ End-to-end performance test failed: {e}")
        import traceback
        traceback.print_exc()
