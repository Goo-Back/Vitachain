# Story: AI Agronomic Recommendations
**Story ID:** 3.5  
**Epic:** 3 - Smart Farming with IoT (KATARA)  
**Status:** ready-for-dev  
**Priority:** P1  

---

## User Story

**As a** Farmer using VitaChain KATARA  
**I want to** receive AI-powered agronomic recommendations based on my IoT sensor data  
**So that** I can make informed decisions about irrigation, fertilization, and crop management to improve yields and reduce resource waste.

---

## Acceptance Criteria (BDD Format)

### AC1: AI Analysis Trigger
```gherkin
Scenario: Farmer triggers AI analysis for their device
  Given I am authenticated as a FARMER
  And I have registered ESP32 devices with telemetry data
  When I POST to "/api/katara/analyze/{device_id}" with optional time range
  Then the system collects telemetry data for the specified period
  And the system calls Claude API with agronomic context
  And I receive 202 status with analysis job ID
  And the analysis completes within 30 seconds (NFR6)
```

### AC2: Recommendation Generation
```gherkin
Scenario: System generates agronomic recommendations
  Given telemetry data shows temperature > 35°C for 3 days
  And humidity < 30% for 48 hours
  And NDVI declining over past week
  When AI analysis is triggered
  Then recommendations include irrigation scheduling
  And recommendations include shade/frost protection
  And recommendations include soil moisture conservation
  And recommendations are specific to Moroccan climate context
```

### AC3: Recommendation Storage & Retrieval
```gherkin
Scenario: Farmer views AI recommendations history
  Given AI analysis has been completed for my device
  When I GET "/api/katara/recommendations/{device_id}"
  Then I receive 200 status with recommendation history
  And each recommendation includes timestamp, analysis, and advice
  And recommendations are ordered by most recent first
  And I can filter by date range
```

### AC4: Alert Integration
```gherkin
Scenario: Critical recommendations create alerts
  Given AI analysis identifies critical conditions
  When recommendations are generated
  Then a high-priority alert is created in katara_alerts table
  And alert includes summary of AI recommendation
  And alert appears in farmer's alert feed
  And alert notification is sent (if configured)
```

### AC5: Data Context Enrichment
```gherkin
Scenario: AI analysis includes environmental context
  Given device has GPS location data
  When AI analysis is triggered
  Then system includes regional climate data for Morocco
  And system includes seasonal crop calendar context
  And system considers local agricultural best practices
  And recommendations are relevant to Moroccan farming
```

---

## Technical Requirements

### Backend Implementation
- **Endpoint:** `POST /api/katara/analyze/{device_id}`
- **Authentication:** JWT Bearer token (FARMER role required)
- **AI Integration:** Claude API via anthropic.AsyncAnthropic()
- **Database:** Direct Supabase client (no SQLAlchemy)
- **Validation:** Pydantic models for request/response
- **Timeout:** 30 seconds for Claude API calls

### Database Schema
```sql
CREATE TABLE ai_recommendations (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id       TEXT NOT NULL,
  farmer_id       UUID REFERENCES profiles(id),
  analysis_period_start TIMESTAMPTZ,
  analysis_period_end   TIMESTAMPTZ,
  telemetry_summary JSONB,  -- Aggregated telemetry data
  ai_response     TEXT,      -- Full Claude API response
  recommendations JSONB,    -- Structured recommendations
  confidence_score FLOAT,   -- AI confidence 0-1
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_recommendations_device_time 
  ON ai_recommendations (device_id, created_at DESC);

CREATE INDEX idx_recommendations_farmer 
  ON ai_recommendations (farmer_id, created_at DESC);

-- RLS Policy
CREATE POLICY "farmers_own_their_recommendations" ON ai_recommendations
FOR ALL USING (farmer_id = auth.uid());
```

### API Contract
**Request:**
```json
{
  "start_date": "2026-04-20T00:00:00Z",  // Optional
  "end_date": "2026-04-27T00:00:00Z",    // Optional
  "analysis_type": "comprehensive"        // Optional: 'comprehensive'|'irrigation'|'health'
}
```

**Response (202):**
```json
{
  "analysis_id": "uuid-...",
  "status": "processing",
  "estimated_completion": "2026-05-03T14:32:00Z"
}
```

**Recommendation Response (200):**
```json
{
  "recommendations": [
    {
      "id": "uuid-...",
      "device_id": "katara-550e8400-e29b-41d4-a716",
      "analysis_period": {
        "start": "2026-04-20T00:00:00Z",
        "end": "2026-04-27T00:00:00Z"
      },
      "telemetry_summary": {
        "avg_temperature": 32.5,
        "avg_humidity": 45.2,
        "ndvi_trend": "declining",
        "data_points": 672
      },
      "ai_response": "Based on the telemetry data analysis...",
      "recommendations": {
        "irrigation": {
          "priority": "high",
          "action": "Increase irrigation frequency to evening hours",
          "reasoning": "High temperatures and low humidity indicate water stress"
        },
        "crop_health": {
          "priority": "medium",
          "action": "Monitor for pest activity in stressed conditions",
          "reasoning": "NDVI decline suggests potential health issues"
        }
      },
      "confidence_score": 0.87,
      "created_at": "2026-05-03T14:30:00Z"
    }
  ]
}
```

---

## Developer Context & Guardrails

### Critical Architecture Rules
```python
# ✅ ALWAYS use async Claude client
from anthropic import AsyncAnthropic
client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

# ✅ ALWAYS extract farmer_id from JWT
farmer_id = get_current_user().id  # From JWT.sub

# ✅ ALWAYS use Supabase client directly
result = supabase.table("ai_recommendations").insert(data).execute()

# ✅ ALWAYS handle Claude API timeouts
try:
    response = await client.messages.create(...)
except asyncio.TimeoutError:
    # Handle timeout gracefully
    pass

# ❌ NEVER use synchronous Claude calls
response = anthropic.Anthropic().messages.create(...)  # BLOCKING

# ❌ NEVER put API keys in code
api_key = "sk-ant-..."  # SECURITY VIOLATION
```

### Claude API Integration Pattern
```python
async def generate_agronomic_recommendations(
    device_id: str, 
    farmer_id: UUID,
    telemetry_data: List[TelemetryReading],
    location: Optional[Tuple[float, float]] = None
) -> AIRecommendation:
    
    # Prepare context for Claude
    context = {
        "role": "expert_agronomist_morocco",
        "location": location,
        "crop_season": get_current_season(),
        "telemetry_summary": aggregate_telemetry(telemetry_data),
        "regional_context": get_moroccan_climate_data(location)
    }
    
    prompt = f"""
    As an expert agronomist specializing in Moroccan agriculture, analyze the following IoT sensor data:
    
    Location: {context['location']} (Morocco)
    Season: {context['crop_season']}
    Data Period: Last 7 days
    
    Telemetry Summary:
    - Average Temperature: {context['telemetry_summary']['avg_temp']}°C
    - Average Humidity: {context['telemetry_summary']['avg_humidity']}%
    - NDVI Trend: {context['telemetry_summary']['ndvi_trend']}
    - Data Points: {context['telemetry_summary']['count']}
    
    Regional Context:
    - Climate Zone: {context['regional_context']['climate_zone']}
    - Typical Crops: {context['regional_context']['common_crops']}
    - Current Season Challenges: {context['regional_context']['seasonal_challenges']}
    
    Provide specific, actionable recommendations for:
    1. Irrigation scheduling and water management
    2. Crop health monitoring and interventions  
    3. Soil conservation and fertilization
    4. Pest and disease prevention
    
    Format your response as structured JSON with priorities and reasoning.
    """
    
    try:
        response = await anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return parse_ai_response(response.content[0].text)
        
    except asyncio.TimeoutError:
        raise AIAnalysisTimeout("Claude API analysis timed out after 30 seconds")
```

### File Structure Requirements
```
backend/app/api/routes/
  └── katara.py              # Add AI analysis endpoint

backend/app/services/
  └── ai_service.py          # Claude API integration logic
  └── agronomic_service.py   # Agriculture-specific business logic

backend/app/models/
  └── schemas.py             # Add AIAnalysis, Recommendation models

backend/app/utils/
  └── climate_data.py        # Moroccan climate context utilities

backend/tests/
  └── test_ai_recommendations.py  # Comprehensive tests
```

---

## Testing Requirements

### Unit Tests
- Claude API prompt generation
- Telemetry data aggregation
- Recommendation parsing and validation
- Timeout handling for Claude API
- Moroccan climate context integration

### Integration Tests
- Complete AI analysis flow
- Error handling for Claude API failures
- Recommendation storage and retrieval
- Alert generation from critical recommendations
- Performance under timeout conditions

### Test Coverage
```python
async def test_ai_analysis_success():
    # Test successful AI recommendation generation

async def test_ai_analysis_timeout():
    # Test 30-second timeout handling

async def test_recommendation_storage():
    # Test recommendation persistence in database

async def test_alert_generation():
    # Test critical recommendations create alerts

async def test_moroccan_context():
    # Test Moroccan climate and season context
```

---

## Performance Requirements

- **Claude API Response:** < 30 seconds (NFR6)
- **Database Query:** Optimized with proper indexes
- **Telemetry Aggregation:** Efficient time-series queries
- **API Response Time:** < 200ms for recommendation retrieval
- **Concurrent Analyses:** Support multiple farmers simultaneously

---

## Security Requirements

### Authentication & Authorization
- JWT token validation (FARMER role required)
- farmer_id extracted from JWT.sub (never from request body)
- RLS policies enforce recommendation data isolation

### API Security
- Claude API key stored in environment variables
- Rate limiting on AI analysis endpoints
- Input validation for date ranges and device IDs

### Data Protection
- All recommendation data linked to authenticated farmer
- No cross-farmer recommendation access possible
- Audit trail via created_at timestamps

---

## Dependencies & Integration

### Internal Dependencies
- Supabase client for database operations
- JWT authentication middleware
- Pydantic for validation
- telemetry_readings table for data source
- katara_alerts table for critical recommendations

### External Dependencies
- **Claude API (Anthropic):** AI analysis generation
- **Timeout:** 30 seconds with fallback handling

### Successor Stories
- 3-6-weather-data-integration: Enhances AI with weather data
- 3-7-satellite-ndvi-imagery: Adds satellite imagery analysis
- 3-20-automatic-ai-recommendation-generation: Scheduled analyses

---

## Project Context Reference

### Technology Stack
- **Backend:** FastAPI + Python 3.11 (async)
- **Database:** Supabase PostgreSQL with RLS
- **Authentication:** Supabase Auth JWT
- **AI:** Claude API via anthropic.AsyncAnthropic()
- **Validation:** Pydantic v2
- **Testing:** pytest with async support

### Code Conventions
- Async/await patterns throughout
- Direct Supabase client usage (no ORM)
- Structured error responses
- Comprehensive logging with structlog
- Environment variable secrets management

### File Locations
- Routes: `backend/app/api/routes/katara.py`
- AI Service: `backend/app/services/ai_service.py`
- Agronomic Service: `backend/app/services/agronomic_service.py`
- Models: `backend/app/models/schemas.py`
- Tests: `backend/tests/test_ai_recommendations.py`

---

## Implementation Notes

### Claude API Integration
- Use anthropic.AsyncAnthropic() for non-blocking calls
- Implement 30-second timeout with graceful fallback
- Structure prompts for consistent JSON responses
- Include Moroccan agricultural context in all analyses

### Recommendation Structure
```json
{
  "irrigation": {
    "priority": "high|medium|low",
    "action": "Specific actionable recommendation",
    "reasoning": "Why this action is needed"
  },
  "crop_health": {
    "priority": "high|medium|low", 
    "action": "Specific actionable recommendation",
    "reasoning": "Why this action is needed"
  },
  "soil_management": {
    "priority": "high|medium|low",
    "action": "Specific actionable recommendation", 
    "reasoning": "Why this action is needed"
  }
}
```

### Moroccan Context
- Include regional climate zones (Mediterranean, Atlantic, Sahara)
- Consider seasonal crop calendars
- Account for water scarcity concerns
- Include local agricultural best practices

### Error Handling
- 408 Request Timeout for Claude API timeouts
- 422 Validation for invalid input parameters
- 403 Forbidden for insufficient permissions
- 500 Internal for unexpected errors (logged)
- 503 Service Unavailable if Claude API is down

---

## Completion Criteria

- [ ] AI analysis API endpoint implemented
- [ ] Claude API integration with async patterns
- [ ] Pydantic models for validation
- [ ] Service layer with AI business logic
- [ ] Moroccan agricultural context integration
- [ ] Recommendation storage and retrieval
- [ ] Alert integration for critical recommendations
- [ ] Comprehensive unit and integration tests
- [ ] 30-second timeout handling
- [ ] RLS policies enforced
- [ ] Error handling complete
- [ ] API documentation updated
- [ ] Performance requirements met
- [ ] Security requirements satisfied

---

## Story Context

This story brings AI-powered agronomic intelligence to the KATARA farming system. By analyzing IoT telemetry data through Claude AI with Moroccan agricultural context, farmers receive:

- **Irrigation Optimization:** Data-driven watering schedules
- **Crop Health Monitoring:** Early detection of stress conditions  
- **Resource Efficiency:** Reduced water and fertilizer waste
- **Yield Improvement:** Science-based farming decisions

The implementation must balance AI accuracy with practical usability, ensuring recommendations are actionable for Moroccan farmers while meeting strict performance and reliability requirements.

This story builds on the telemetry foundation (stories 3-1 to 3-4) and enables future enhancements with weather data and satellite imagery.

---

**Last Updated:** 2026-05-03T23:50:00Z  
**Next Story:** 3-6-weather-data-integration  
**Dependencies:** Stories 3-1 through 3-4 must be complete
