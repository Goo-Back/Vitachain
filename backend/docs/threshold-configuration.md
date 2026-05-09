# Threshold-Based Alert Configuration

## Overview

The KATARA threshold-based alert system automatically generates alerts when IoT sensor readings exceed predefined thresholds. This document explains how to configure and customize these thresholds.

## Environment Variables

The threshold system uses the following environment variables for configuration:

### Temperature Threshold

```bash
ALERT_TEMPERATURE_HIGH=40.0
```

- **Description**: High temperature threshold in Celsius
- **Default**: `40.0`
- **Range**: `-10.0` to `60.0`
- **Alert Severity**: `high`
- **Trigger**: When temperature > threshold
- **Alert Message**: "Critical temperature detected: {value}°C (threshold: {threshold}°C). Immediate action recommended to prevent heat stress."

### Humidity Threshold

```bash
ALERT_HUMIDITY_LOW=20.0
```

- **Description**: Low humidity threshold in percentage
- **Default**: `20.0`
- **Range**: `0.0` to `100.0`
- **Alert Severity**: `high`
- **Trigger**: When humidity < threshold
- **Alert Message**: "Low humidity detected: {value}% (threshold: {threshold}%). Risk of dehydration - consider irrigation."

### NDVI Threshold

```bash
ALERT_NDVI_LOW=0.3
```

- **Description**: Low NDVI threshold for vegetation stress detection
- **Default**: `0.3`
- **Range**: `-1.0` to `1.0`
- **Alert Severity**: `medium`
- **Trigger**: When NDVI < threshold
- **Alert Message**: "Vegetation stress detected: NDVI {value} (threshold: {threshold}). Review irrigation and nutrient levels."

## Configuration Examples

### Default Configuration
```bash
# Use default thresholds
# No environment variables needed - defaults will be used
```

### Custom Configuration
```bash
# Custom thresholds for specific crop requirements
ALERT_TEMPERATURE_HIGH=35.0    # More sensitive to heat
ALERT_HUMIDITY_LOW=30.0        # More sensitive to dryness
ALERT_NDVI_LOW=0.4            # Earlier vegetation stress detection
```

### Tropical Climate Configuration
```bash
# Adjusted for tropical climate conditions
ALERT_TEMPERATURE_HIGH=45.0    # Higher heat tolerance
ALERT_HUMIDITY_LOW=40.0        # Higher humidity expectations
ALERT_NDVI_LOW=0.25            # Lower NDVI threshold for dense vegetation
```

## Implementation Details

### Threshold Service

The `ThresholdService` class handles all threshold validation logic:

```python
from app.services.threshold_service import get_threshold_service

# Get configured threshold service
threshold_service = get_threshold_service()

# Check all thresholds
violations = threshold_service.check_all_thresholds(
    temperature=42.0,
    humidity=15.0,
    ndvi=0.25
)
```

### Alert Integration

The alert service automatically uses the threshold service for alert generation:

```python
from app.services.alert_service import AlertService

# Alert service automatically integrates with threshold service
alert_service = AlertService(supabase_client)

# This will automatically check thresholds and create alerts
response = await alert_service.check_thresholds_and_create_alerts(
    device_id="device-123",
    farmer_id=farmer_uuid,
    temperature=42.0,
    humidity=15.0,
    ndvi=0.25
)
```

### Performance Requirements

The threshold system is optimized for performance:

- **Threshold Checking**: < 5ms per check (actual: ~0.03ms average)
- **Alert Generation**: < 15ms total impact on telemetry processing
- **Memory Efficiency**: Minimal footprint with proper object management
- **Concurrent Processing**: Efficient handling of multiple devices

### Error Handling

The system gracefully handles various error conditions:

- **Invalid Values**: NaN, infinity, out-of-range values are ignored
- **Missing Environment Variables**: Falls back to default values
- **Database Failures**: Alert failures don't affect telemetry processing
- **Configuration Errors**: Invalid environment variables use defaults

## Monitoring and Troubleshooting

### Logging

The threshold service provides structured logging:

```python
# Example log entries
{
  "event": "temperature_alert_created",
  "device_id": "device-123",
  "temperature": 42.5,
  "threshold": 40.0
}

{
  "event": "threshold_config_updated",
  "new_config": {
    "temperature_high": 45.0,
    "humidity_low": 15.0,
    "ndvi_low": 0.25
  }
}
```

### Performance Monitoring

Monitor the following metrics:

- Threshold checking latency
- Alert generation rate
- False positive rate
- Configuration validation errors

### Common Issues

1. **Environment Variables Not Loading**
   - Verify environment variables are set before application startup
   - Check for typos in variable names
   - Ensure proper .env file loading

2. **No Alerts Generated**
   - Verify thresholds are appropriate for your use case
   - Check sensor data validity
   - Review alert service logs

3. **Performance Issues**
   - Monitor threshold checking latency
   - Check for excessive concurrent processing
   - Verify database performance

## Testing

### Unit Tests
```bash
# Run threshold service tests
python -m pytest tests/test_threshold_service.py -v

# Run alert system integration tests
python -m pytest tests/test_alert_system.py::TestAlertThresholdIntegration -v
```

### Performance Tests
```bash
# Run performance validation
python test_threshold_performance_only.py
```

### Configuration Tests
```bash
# Test with custom environment variables
ALERT_TEMPERATURE_HIGH=45.0 python test_threshold_integration.py
```

## Security Considerations

- **Environment Variables**: Store sensitive configuration securely
- **Validation**: All threshold values are validated before use
- **Error Isolation**: Threshold checking failures don't affect core system functionality
- **Audit Trail**: All configuration changes are logged

## Future Enhancements

Potential future improvements:

1. **Dynamic Thresholds**: Time-based or crop-specific thresholds
2. **Machine Learning**: Adaptive threshold optimization
3. **Multi-level Alerts**: Warning, critical, and emergency severity levels
4. **Geographic Variations**: Location-based threshold adjustments
5. **Historical Analysis**: Threshold effectiveness analytics

## Support

For issues or questions about threshold configuration:

1. Check the application logs for detailed error messages
2. Verify environment variable configuration
3. Run the provided test suites for validation
4. Consult the development team for custom threshold requirements
