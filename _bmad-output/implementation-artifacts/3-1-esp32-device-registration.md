# Story: ESP32 Device Registration
**Story ID:** 3.1  
**Epic:** 3 - Smart Farming with IoT (KATARA)  
**Status:** ready-for-dev  
**Priority:** P0  

---

## User Story

**As a** Farmer using VitaChain KATARA  
**I want to** register my ESP32 IoT devices in the system  
**So that** I can monitor my agricultural fields in real-time and receive alerts about critical conditions.

---

## Acceptance Criteria (BDD Format)

### AC1: Device Registration API
```gherkin
Scenario: Farmer registers a new ESP32 device
  Given I am authenticated as a FARMER
  When I POST to "/api/katara/devices" with device details
    - device_id: "katara-{uuid4}" (unique)
    - name: "Parcelle Nord" (optional)
    - location_lat: 33.5 (optional)
    - location_lng: -7.6 (optional)
  Then the device is registered in iot_devices table
  And the device is linked to my farmer_id from JWT
  And I receive 201 status with device details
  And the device appears in my devices list
```

### AC2: Device Validation
```gherkin
Scenario: System validates device registration data
  Given I am authenticated as a FARMER
  When I POST to "/api/katara/devices" with invalid data
  Then I receive 422 validation error
  And the device is not created
```

### AC3: Device ID Uniqueness
```gherkin
Scenario: System prevents duplicate device IDs
  Given I have registered device "katara-123"
  When I try to register another device with same ID
  Then I receive 409 conflict error
  And the original device remains unchanged
```

### AC4: Device Listing
```gherkin
Scenario: Farmer views their registered devices
  Given I am authenticated as a FARMER
  And I have registered 2 devices
  When I GET "/api/katara/devices"
  Then I receive 200 status
  And I see both my devices
  And I don't see devices from other farmers
```

### AC5: Authorization Enforcement
```gherkin
Scenario: Non-farmer cannot register devices
  Given I am authenticated as RESTAURANT
  When I POST to "/api/katara/devices"
  Then I receive 403 forbidden error
  And no device is created
```

---

## Technical Requirements

### Backend Implementation
- **Endpoint:** `POST /api/katara/devices`
- **Authentication:** JWT Bearer token (FARMER role required)
- **Database:** Direct Supabase client (no SQLAlchemy)
- **Validation:** Pydantic models for request/response
- **Error Handling:** Structured error responses

### Database Schema
```sql
CREATE TABLE iot_devices (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id     TEXT UNIQUE NOT NULL,      -- 'katara-{uuid4}'
  farmer_id     UUID REFERENCES profiles(id),
  name          TEXT,                       -- 'Parcelle Nord'
  location_lat  FLOAT,
  location_lng  FLOAT,
  registered_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policy
CREATE POLICY "farmers_own_their_devices" ON iot_devices
FOR ALL USING (farmer_id = auth.uid());
```

### API Contract
**Request:**
```json
{
  "device_id": "katara-550e8400-e29b-41d4-a716",
  "name": "Parcelle Nord",
  "location_lat": 33.5,
  "location_lng": -7.6
}
```

**Response (201):**
```json
{
  "id": "uuid-...",
  "device_id": "katara-550e8400-e29b-41d4-a716",
  "name": "Parcelle Nord",
  "location_lat": 33.5,
  "location_lng": -7.6,
  "registered_at": "2026-05-03T14:30:00Z"
}
```

---

## Developer Context & Guardrails

### Critical Architecture Rules
```python
# ✅ ALWAYS extract farmer_id from JWT
farmer_id = get_current_user().id  # From JWT.sub

# ✅ ALWAYS use Supabase client directly
result = supabase.table("iot_devices").insert(data).execute()

# ✅ ALWAYS use async patterns
async def register_device(device_data: DeviceCreate, farmer_id: UUID):
    # Implementation here

# ❌ NEVER trust farmer_id from request body
farmer_id = request.body.farmer_id  # SECURITY VIOLATION
```

### File Structure Requirements
```
backend/app/api/routes/
  └── katara.py              # Add device registration endpoint

backend/app/services/
  └── device_service.py       # Device registration logic

backend/app/models/
  └── schemas.py             # Add DeviceCreate, DeviceResponse models

backend/tests/
  └── test_device_registration.py  # Comprehensive tests
```

### Implementation Patterns
```python
# Pydantic Models
class DeviceCreate(BaseModel):
    device_id: str = Field(..., regex=r'^katara-[a-f0-9-]{36}$')
    name: Optional[str] = Field(None, max_length=100)
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lng: Optional[float] = Field(None, ge=-180, le=180)

class DeviceResponse(BaseModel):
    id: UUID
    device_id: str
    farmer_id: UUID
    name: Optional[str]
    location_lat: Optional[float]
    location_lng: Optional[float]
    registered_at: datetime

# Service Layer
async def register_device(device_data: DeviceCreate, farmer_id: UUID) -> DeviceResponse:
    # Check device_id uniqueness
    existing = supabase.table("iot_devices").select("id").eq("device_id", device_data.device_id).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Device ID already exists")
    
    # Insert device
    device_record = {
        "device_id": device_data.device_id,
        "farmer_id": str(farmer_id),
        "name": device_data.name,
        "location_lat": device_data.location_lat,
        "location_lng": device_data.location_lng
    }
    
    result = supabase.table("iot_devices").insert(device_record).execute()
    return DeviceResponse(**result.data[0])
```

---

## Testing Requirements

### Unit Tests
- Device validation with Pydantic models
- Device ID uniqueness checking
- Farmer ID extraction from JWT
- Supabase client interactions

### Integration Tests
- Complete device registration flow
- Error handling for invalid data
- Authorization enforcement (different roles)
- Device listing with proper filtering

### Test Coverage
```python
async def test_register_device_success():
    # Test successful device registration

async def test_register_device_duplicate_id():
    # Test device ID uniqueness constraint

async def test_register_device_unauthorized_role():
    # Test non-farmer cannot register devices

async def test_list_devices_only_owned():
    # Test farmers only see their own devices
```

---

## Performance Requirements

- **API Response Time:** < 200ms (P95)
- **Database Query:** Optimized with proper indexes
- **Validation:** Fast Pydantic model validation
- **Error Handling:** Graceful degradation

---

## Security Requirements

### Authentication & Authorization
- JWT token validation (FARMER role required)
- farmer_id extracted from JWT.sub (never from request body)
- RLS policies enforce data isolation

### Input Validation
- device_id format: `katara-{uuid4}` regex validation
- Location coordinates: Valid latitude/longitude ranges
- Name length: Maximum 100 characters

### Data Protection
- All device data linked to authenticated farmer
- No cross-farmer data access possible
- Audit trail via created_at timestamps

---

## Dependencies & Integration

### Internal Dependencies
- Supabase client for database operations
- JWT authentication middleware
- Pydantic for validation
- FastAPI for API framework

### External Dependencies
- None (this story is self-contained)

### Successor Stories
- 3-2-telemetry-data-ingestion: Uses registered devices for telemetry
- 3-3-real-time-dashboard: Displays device data
- Future stories will build on device registration foundation

---

## Project Context Reference

### Technology Stack
- **Backend:** FastAPI + Python 3.11 (async)
- **Database:** Supabase PostgreSQL with RLS
- **Authentication:** Supabase Auth JWT
- **Validation:** Pydantic v2
- **Testing:** pytest with async support

### Code Conventions
- Async/await patterns throughout
- Direct Supabase client usage (no ORM)
- Structured error responses
- Comprehensive logging with structlog

### File Locations
- Routes: `backend/app/api/routes/katara.py`
- Services: `backend/app/services/device_service.py`
- Models: `backend/app/models/schemas.py`
- Tests: `backend/tests/test_device_registration.py`

---

## Implementation Notes

### Device ID Generation
- Device IDs must follow pattern: `katara-{uuid4}`
- UUID4 generated by ESP32 device or backend
- Pattern enforced via regex validation

### Location Data
- Optional latitude/longitude for device placement
- Stored as float values with range validation
- Used for future mapping features

### Error Handling
- 409 Conflict for duplicate device IDs
- 422 Validation for invalid input data
- 403 Forbidden for insufficient permissions
- 500 Internal for unexpected errors (logged)

---

## Completion Criteria

- [ ] Device registration API endpoint implemented
- [ ] Pydantic models for validation
- [ ] Service layer with business logic
- [ ] Comprehensive unit and integration tests
- [ ] RLS policies enforced
- [ ] Error handling complete
- [ ] API documentation updated
- [ ] Performance requirements met
- [ ] Security requirements satisfied

---

## Story Context

This story establishes the foundation for the entire KATARA IoT system. Device registration enables:
- Real-time telemetry collection (story 3-2)
- Dashboard visualization (story 3-3)
- AI agronomic analysis (story 3-5)
- Alert system functionality (story 3-8)

The implementation must be robust and secure as it's the entry point for all IoT data flows in the VitaChain platform.

---

**Last Updated:** 2026-05-03T10:40:00Z  
**Next Story:** 3-2-telemetry-data-ingestion  
**Dependencies:** Epic 2 (User Authentication) must be complete
