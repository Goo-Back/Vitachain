# Story: Telemetry Data Ingestion
**Story ID:** 3.2  
**Epic:** 3 - Smart Farming with IoT (KATARA)  
**Status:** ready-for-dev  
**Priority:** P0  

---

## User Story

**As a** Farmer using VitaChain KATARA  
**I want to** receive real-time telemetry data from my ESP32 devices  
**So that** I can monitor my agricultural conditions and receive timely alerts about critical situations.

---

## Acceptance Criteria (BDD Format)

### AC1: Telemetry Ingestion API
```gherkin
Scenario: ESP32 device sends telemetry data
  Given I have a registered ESP32 device with valid API key
  When I POST to "/api/telemetry" with sensor readings
    - device_id: "katara-{uuid4}" (registered device)
    - temperature: 36.8 (float, -10 to 60°C)
    - humidity: 55.2 (float, 0 to 100%)
    - ndvi: 0.42 (float, -1 to 1)
    - battery_level: 78.5 (float, 0 to 100%)
    - timestamp: "2026-05-03T14:30:00Z" (ISO 8601)
  Then the data is stored in telemetry_readings table
  And the device is validated as belonging to a farmer
  And I receive 200 status with reading confirmation
  And processing time is < 50ms (NFR1)
```

### AC2: API Key Authentication
```gherkin
Scenario: System validates telemetry API key
  Given I am sending telemetry data
  When I POST to "/api/telemetry" without valid X-API-Key header
  Then I receive 401 unauthorized error
  And no data is stored
  And the request is logged for security monitoring
```

### AC3: Device Validation
```gherkin
Scenario: System validates device ownership
  Given I have a valid API key for device "katara-123"
  When I POST to "/api/telemetry" with device_id "katara-456" (different device)
  Then I receive 403 forbidden error
  And no data is stored
  And the mismatch is logged for security
```

### AC4: Data Validation
```gherkin
Scenario: System validates telemetry data ranges
  Given I have a valid device and API key
  When I POST to "/api/telemetry" with invalid data
    - temperature: 200 (out of range)
    - humidity: -10 (out of range)
    - ndvi: 2.0 (out of range)
  Then I receive 422 validation error
  And no data is stored
  And validation errors are detailed
```

### AC5: High-Performance Processing
```gherkin
Scenario: System processes telemetry within performance requirements
  Given I have a valid device and API key
  When I POST to "/api/telemetry" with valid data
  Then the response time is < 50ms
  And database insertion is optimized
  And async processing is used throughout
```

### AC6: Threshold Alert Triggering
```gherkin
Scenario: System triggers alerts for critical conditions
  Given I have a valid device and API key
  When I POST to "/api/telemetry" with critical values
    - temperature: 42°C (> 40°C threshold)
    - humidity: 15% (< 20% threshold)
    - ndvi: 0.25 (< 0.3 threshold)
  Then alerts are created in katara_alerts table
  And alert severity is set appropriately
  And farmer is notified of critical conditions
```

---

## Technical Requirements

### Backend Implementation
- **Endpoint:** `POST /api/telemetry`
- **Authentication:** X-API-Key header (IoT device authentication)
- **Database:** Direct Supabase client with service_role for bypassing RLS
- **Validation:** Pydantic models for request/response
- **Performance:** Async processing with < 50ms response time
- **Error Handling:** Structured error responses

### Database Schema
```sql
CREATE TABLE telemetry_readings (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id     TEXT NOT NULL,
  farmer_id     UUID REFERENCES profiles(id),
  temperature   FLOAT CHECK (temperature BETWEEN -10 AND 60),
  humidity      FLOAT CHECK (humidity BETWEEN 0 AND 100),
  ndvi          FLOAT CHECK (ndvi BETWEEN -1 AND 1),
  battery_level FLOAT,
  timestamp     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_telemetry_device_time
  ON telemetry_readings (device_id, timestamp DESC);

CREATE INDEX idx_telemetry_farmer
  ON telemetry_readings (farmer_id, timestamp DESC);

-- RLS Policy (bypassed for service_role insertion)
CREATE POLICY "farmers_read_their_telemetry" ON telemetry_readings FOR SELECT
  USING (farmer_id = auth.uid() OR auth.jwt()->>'role' = 'ADMIN');
```

### API Contract
**Request Headers:**
```
X-API-Key: <device_api_key>
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_id": "katara-550e8400-e29b-41d4-a716",
  "temperature": 36.8,
  "humidity": 55.2,
  "ndvi": 0.42,
  "battery_level": 78.5,
  "timestamp": "2026-05-03T14:30:00Z"
}
```

**Response (200):**
```json
{
  "status": "ok",
  "reading_id": "uuid-...",
  "farmer_notified": false,
  "alerts_triggered": 1,
  "processing_time_ms": 23
}
```

---

## Developer Context & Guardrails

### Critical Architecture Rules
```python
# ✅ ALWAYS use service_role for telemetry insertion
supabase_client = get_supabase_client(service_role=True)

# ✅ ALWAYS validate API key against devices table
device = validate_api_key(api_key)
farmer_id = device['farmer_id']

# ✅ ALWAYS use async patterns
async def ingest_telemetry(telemetry_data: TelemetryCreate):
    # Async implementation here

# ✅ ALWAYS validate device ownership
if telemetry_data.device_id != device['device_id']:
    raise HTTPException(status_code=403)

# ❌ NEVER trust device_id from request body without validation
# ❌ NEVER use regular client for telemetry insertion (RLS blocks it)
# ❌ NEVER process telemetry synchronously (performance requirement)
```

### File Structure Requirements
```
backend/app/api/routes/
  └── telemetry.py              # New telemetry ingestion endpoint

backend/app/services/
  └── telemetry_service.py      # Telemetry processing logic
  └── alert_service.py          # Alert triggering logic

backend/app/models/
  └── schemas.py                # Add TelemetryCreate, TelemetryResponse models

backend/app/core/
  └── database.py               # Add service_role client support

backend/tests/
  └── test_telemetry_ingestion.py  # Comprehensive tests
```

### Implementation Patterns
```python
# Pydantic Models
class TelemetryCreate(BaseModel):
    device_id: str = Field(..., pattern=r'^katara-[a-f0-9-]{36}$')
    temperature: float = Field(..., ge=-10, le=60)
    humidity: float = Field(..., ge=0, le=100)
    ndvi: float = Field(..., ge=-1, le=1)
    battery_level: Optional[float] = Field(None, ge=0, le=100)
    timestamp: Optional[datetime] = Field(None)  # Defaults to NOW()

class TelemetryResponse(BaseModel):
    status: str = "ok"
    reading_id: UUID
    farmer_notified: bool = False
    alerts_triggered: int = 0
    processing_time_ms: int

# Service Layer
async def ingest_telemetry(telemetry_data: TelemetryCreate, api_key: str) -> TelemetryResponse:
    start_time = time.time()
    
    # Validate API key and get device
    device = await validate_device_api_key(api_key)
    if device['device_id'] != telemetry_data.device_id:
        raise HTTPException(status_code=403, detail="Device ID mismatch")
    
    # Insert telemetry using service_role
    supabase = get_supabase_client(service_role=True)
    reading_data = {
        "device_id": telemetry_data.device_id,
        "farmer_id": device['farmer_id'],
        "temperature": telemetry_data.temperature,
        "humidity": telemetry_data.humidity,
        "ndvi": telemetry_data.ndvi,
        "battery_level": telemetry_data.battery_level,
        "timestamp": telemetry_data.timestamp or datetime.utcnow()
    }
    
    result = supabase.table("telemetry_readings").insert(reading_data).execute()
    reading_id = result.data[0]['id']
    
    # Check for threshold alerts
    alerts_triggered = await check_threshold_alerts(telemetry_data, device['farmer_id'])
    
    processing_time = int((time.time() - start_time) * 1000)
    return TelemetryResponse(
        reading_id=reading_id,
        alerts_triggered=alerts_triggered,
        processing_time_ms=processing_time
    )
```

---

## Testing Requirements

### Unit Tests
- Telemetry data validation with Pydantic models
- API key validation against devices table
- Device ownership verification
- Threshold alert calculation logic
- Performance measurement (< 50ms requirement)

### Integration Tests
- Complete telemetry ingestion flow
- Error handling for invalid API keys
- Error handling for device ID mismatches
- Database insertion with service_role client
- Alert triggering for threshold violations

### Performance Tests
- Load testing with 1000 concurrent requests
- Response time validation under load
- Database performance with high volume
- Memory usage during sustained load

### Test Coverage
```python
async def test_telemetry_ingestion_success():
    # Test successful telemetry ingestion

async def test_telemetry_invalid_api_key():
    # Test API key validation

async def test_telemetry_device_mismatch():
    # Test device ownership validation

async def test_telemetry_threshold_alerts():
    # Test alert triggering

async def test_telemetry_performance_requirement():
    # Test < 50ms processing time
```

---

## Performance Requirements

### Response Time Targets
- **API Response:** < 50ms (NFR1 requirement)
- **Database Insert:** < 20ms (optimized with indexes)
- **Validation:** < 5ms (Pydantic model validation)
- **Alert Processing:** < 10ms (threshold checking)

### Scalability Requirements
- **Concurrent Requests:** Support 1000+ concurrent telemetry submissions
- **Throughput:** Handle 10,000 readings/minute
- **Database Optimization:** Time-series indexes for fast queries
- **Memory Efficiency:** Minimal memory footprint per request

### Monitoring Requirements
- Response time tracking
- Error rate monitoring
- Database performance metrics
- Alert generation statistics

---

## Security Requirements

### Authentication & Authorization
- API key validation for each request
- Device ownership verification
- Service role database access for insertion
- Rate limiting per device to prevent abuse

### Input Validation
- Device ID format validation
- Sensor value range validation
- Timestamp format validation
- SQL injection prevention via parameterized queries

### Data Protection
- All telemetry linked to authenticated farmer
- Audit trail via timestamps and device IDs
- No cross-farmer data access possible
- Secure API key storage and rotation

### Threat Protection
```python
# Rate limiting per device
@router.post("/api/telemetry", dependencies=[Depends(rate_limit_per_device)])

# API key validation
async def validate_device_api_key(api_key: str) -> dict:
    device = supabase.table("iot_devices").select("*").eq("api_key", api_key).execute()
    if not device.data:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return device.data[0]

# Device ownership check
if telemetry_data.device_id != device['device_id']:
    raise HTTPException(status_code=403, detail="Device ID mismatch")
```

---

## Dependencies & Integration

### Internal Dependencies
- Supabase service_role client for database operations
- Device registration data from iot_devices table
- Alert system integration for threshold violations
- Performance monitoring and logging

### External Dependencies
- None (self-contained telemetry ingestion)

### Successor Stories
- 3-3-real-time-dashboard: Uses ingested telemetry for visualization
- 3-4-telemetry-history-trend-analysis: Historical analysis of ingested data
- 3-5-ai-agronomic-recommendations: AI analysis of telemetry patterns
- 3-8-critical-condition-alert-system: Enhanced alert functionality

---

## Project Context Reference

### Technology Stack
- **Backend:** FastAPI + Python 3.11 (async)
- **Database:** Supabase PostgreSQL with service_role access
- **Authentication:** API key-based for IoT devices
- **Validation:** Pydantic v2 with strict type checking
- **Performance:** Async processing with < 50ms target

### Code Conventions
- Async/await patterns throughout
- Direct Supabase client usage (no ORM)
- Service role for bypassing RLS in telemetry insertion
- Structured error responses with detailed codes
- Comprehensive logging with performance metrics

### File Locations
- Routes: `backend/app/api/routes/telemetry.py` (new file)
- Services: `backend/app/services/telemetry_service.py` (new file)
- Models: `backend/app/models/schemas.py` (extend existing)
- Database: `backend/app/core/database.py` (extend for service_role)
- Tests: `backend/tests/test_telemetry_ingestion.py` (new file)

---

## Implementation Notes

### API Key Management
- API keys generated during device registration (story 3-1)
- Keys stored in iot_devices table
- Rotation policy: every 90 days (NFR requirement)
- Secure key generation using secrets.token_urlsafe()

### Threshold Alert Logic
```python
THRESHOLDS = {
    "temperature_high": 40.0,    # °C
    "humidity_low": 20.0,        # %
    "ndvi_low": 0.3,            # Vegetation stress
}

async def check_threshold_alerts(telemetry: TelemetryCreate, farmer_id: UUID) -> int:
    alerts_count = 0
    
    if telemetry.temperature > THRESHOLDS["temperature_high"]:
        await create_alert(farmer_id, "threshold_exceeded", "high", 
                          f"Temperature critical: {telemetry.temperature}°C")
        alerts_count += 1
    
    if telemetry.humidity < THRESHOLDS["humidity_low"]:
        await create_alert(farmer_id, "threshold_exceeded", "high",
                          f"Humidity critical: {telemetry.humidity}%")
        alerts_count += 1
    
    if telemetry.ndvi < THRESHOLDS["ndvi_low"]:
        await create_alert(farmer_id, "threshold_exceeded", "medium",
                          f"NDVI stress detected: {telemetry.ndvi}")
        alerts_count += 1
    
    return alerts_count
```

### Database Optimization
- Time-series indexes on (device_id, timestamp)
- Farmer-specific indexes for quick dashboard queries
- Partitioning strategy for large-scale deployments
- Connection pooling for high throughput

### Error Handling Strategy
- 401 Unauthorized for invalid API keys
- 403 Forbidden for device ownership mismatches
- 422 Validation for out-of-range sensor values
- 500 Internal for unexpected database errors
- Detailed logging for all error conditions

---

## Completion Criteria

- [ ] Telemetry ingestion API endpoint implemented
- [ ] API key authentication system
- [ ] Device ownership validation
- [ ] Pydantic models for telemetry validation
- [ ] Service role database integration
- [ ] Threshold alert triggering logic
- [ ] Performance optimization (< 50ms response)
- [ ] Comprehensive unit and integration tests
- [ ] Error handling and logging complete
- [ ] Security requirements satisfied
- [ ] API documentation updated
- [ ] Load testing completed

---

## Story Context

This story is the critical data pipeline for the entire KATARA IoT system. Telemetry ingestion enables:
- Real-time monitoring (story 3-3)
- Historical trend analysis (story 3-4)
- AI agronomic recommendations (story 3-5)
- Critical condition alerts (story 3-8)

The implementation must meet strict performance requirements (< 50ms) as this is the highest frequency API in the system, potentially handling thousands of requests per minute from deployed ESP32 devices.

---

**Last Updated:** 2026-05-03T22:49:00Z  
**Previous Story:** 3-1-esp32-device-registration (completed)  
**Next Story:** 3-3-real-time-dashboard  
**Dependencies:** Epic 2 (User Authentication) and Story 3-1 must be complete
