# Story: Automatic AI Recommendation Generation
**Story ID:** 3.10  
**Epic:** 3 - Smart Farming with IoT (KATARA)  
**Status:** done  
**Priority:** P1  

---

## User Story

**As a** Farmer using VitaChain KATARA  
**I want to** automatically receive AI-powered agronomic recommendations when my IoT sensors detect critical conditions  
**So that** I can take proactive action to protect my crops without manually requesting analysis, ensuring timely intervention when my plants need it most.

---

## Acceptance Criteria (BDD Format)

### AC1: Automatic AI Analysis Trigger on Critical Thresholds
```gherkin
Scenario: System automatically triggers AI analysis when critical thresholds are exceeded
  Given I am authenticated as a FARMER
  And my ESP32 device sends telemetry data
  When temperature exceeds 40°C OR humidity drops below 20% OR NDVI drops below 0.3
  Then the system automatically triggers AI analysis for the affected device
  And analysis uses the last 7 days of telemetry data
  And analysis includes current critical condition context
  And AI recommendation is generated within 30 seconds (NFR6)
  And a high-priority alert is created with AI recommendation summary
```

### AC2: AI Recommendation Integration with Alert System
```gherkin
Scenario: Critical alerts include AI-generated recommendations
  Given automatic AI analysis is triggered by critical conditions
  When AI recommendations are generated
  Then the recommendations are stored in ai_recommendations table
  And a katara_alert is created with type 'ai_recommendation'
  And alert severity reflects the most critical condition detected
  And alert message includes actionable AI recommendations summary
  And alert includes link to full AI analysis details
```

### AC3: Periodic Proactive Analysis for Optimal Conditions
```gherkin
Scenario: System performs periodic AI analysis during optimal growing conditions
  Given I am authenticated as a FARMER
  And my device has been active for more than 7 days
  And no critical conditions are detected in the last 24 hours
  When the system daily analysis job runs
  Then AI analysis is automatically triggered for my device
  And analysis focuses on optimization opportunities
  And recommendations are stored with priority 'medium'
  And alert is created only if recommendations contain significant insights
```

### AC4: Intelligent Analysis Frequency Control
```gherkin
Scenario: System prevents AI analysis spam while ensuring responsiveness
  Given AI analysis has been performed for my device in the last 6 hours
  When new critical conditions are detected
  Then the system checks if conditions have significantly changed (>10% variance)
  And if conditions are similar, existing recommendations are reused
  And if conditions are significantly different, new analysis is triggered
  And analysis frequency never exceeds once per 2 hours per device
```

### AC5: Context-Enriched Automatic Analysis
```gherkin
Scenario: Automatic AI analysis includes full environmental context
  Given automatic AI analysis is triggered
  When the analysis is performed
  Then system includes current weather data from OpenWeatherMap
  And system includes recent NDVI trends if available
  And system includes seasonal context for Moroccan agriculture
  And system includes device location and crop type context
  And recommendations are specific to current conditions and location
```

### AC6: Farmer Notification and Control
```gherkin
Scenario: Farmers receive notifications and can control automatic analysis
  Given automatic AI analysis generates recommendations
  When recommendations are created
  Then I receive real-time notification via Supabase Realtime
  And I can view all automatic recommendations in my dashboard
  And I can disable automatic analysis per device if desired
  And I can manually trigger analysis regardless of automatic schedule
  And system respects my preferences for analysis frequency
```

---

## Technical Requirements

### Backend Implementation
- **Trigger Points:** Enhanced `/api/telemetry` endpoint and scheduled background job
- **AI Integration:** Reuse existing Claude API patterns from story 3-5
- **Database:** Direct Supabase client integration with ai_recommendations and katara_alerts tables
- **Scheduling:** Background job using FastAPI BackgroundTasks or APScheduler
- **Rate Limiting:** Intelligent frequency control per device
- **Context Enrichment:** Integration with weather API and NDVI data

### Database Schema Extensions
```sql
-- Add to ai_recommendations table (from story 3-5)
ALTER TABLE ai_recommendations 
ADD COLUMN trigger_type TEXT CHECK (trigger_type IN ('manual','automatic_critical','automatic_periodic')),
ADD COLUMN trigger_conditions JSONB,  -- What triggered this analysis
ADD COLUMN analysis_priority TEXT CHECK (analysis_priority IN ('low','medium','high','critical')),
ADD COLUMN auto_analysis_enabled BOOLEAN DEFAULT TRUE;

-- Add to iot_devices table
ALTER TABLE iot_devices 
ADD COLUMN auto_analysis_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN last_auto_analysis TIMESTAMPTZ,
ADD COLUMN analysis_frequency_hours INT DEFAULT 6;

-- Index for efficient automatic analysis queries
CREATE INDEX idx_recommendations_device_trigger_time 
  ON ai_recommendations (device_id, trigger_type, created_at DESC);

CREATE INDEX idx_devices_auto_analysis 
  ON iot_devices (auto_analysis_enabled, last_auto_analysis);
```

### API Contract Enhancements
**Device Settings Update:**
```json
// PATCH /api/katara/devices/{device_id}/settings
{
  "auto_analysis_enabled": true,
  "analysis_frequency_hours": 6,
  "critical_threshold_only": false
}
```

**Automatic Analysis Response (in alert feed):**
```json
{
  "alert": {
    "id": "uuid-...",
    "type": "ai_recommendation",
    "severity": "high",
    "message": "Critical heat stress detected - Immediate evening irrigation recommended",
    "created_at": "2026-05-03T14:30:00Z",
    "is_read": false,
    "device_id": "katara-550e8400-e29b-41d4-a716",
    "recommendation_id": "uuid-...",
    "trigger_conditions": {
      "temperature": 42.5,
      "humidity": 18.2,
      "threshold_exceeded": "temperature"
    }
  }
}
```

---

## Developer Context & Guardrails

### Critical Architecture Rules
```python
# ✅ ALWAYS reuse existing AI service patterns
from app.services.ai_service import generate_agronomic_recommendations
from app.services.alert_service import create_alert

# ✅ ALWAYS extract farmer_id from JWT
farmer_id = get_current_user().id  # From JWT.sub

# ✅ ALWAYS use async patterns for AI calls
recommendations = await generate_agronomic_recommendations(...)

# ✅ ALWAYS check analysis frequency limits
if await should_allow_auto_analysis(device_id, farmer_id):
    await trigger_auto_analysis(device_id, farmer_id)

# ✅ ALWAYS include trigger context
trigger_context = {
    "type": "automatic_critical",
    "conditions": {
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "threshold_exceeded": ["temperature"]
    }
}

# ❌ NEVER trigger analysis without rate limiting
await trigger_auto_analysis(device_id)  # SPAM RISK

# ❌ NEVER ignore farmer preferences
if device.auto_analysis_enabled:  # GOOD
# Always check farmer settings first
```

### Automatic Analysis Trigger Pattern
```python
async def handle_automatic_analysis_trigger(
    device_id: str,
    farmer_id: UUID,
    telemetry_reading: TelemetryReading,
    trigger_type: str = "critical_threshold"
):
    """Handle automatic AI analysis trigger with intelligent rate limiting"""
    
    # Check if auto-analysis is enabled for this device
    device_settings = await get_device_analysis_settings(device_id, farmer_id)
    if not device_settings.auto_analysis_enabled:
        return
    
    # Check rate limiting and analysis frequency
    if not await should_allow_auto_analysis(device_id, farmer_id):
        logger.info(f"Rate limited auto-analysis for device {device_id}")
        return
    
    # Check if conditions have significantly changed since last analysis
    if not await conditions_significantly_changed(device_id, telemetry_reading):
        logger.info(f"Conditions unchanged, skipping auto-analysis for {device_id}")
        return
    
    try:
        # Trigger AI analysis with full context
        recommendations = await generate_agronomic_recommendations(
            device_id=device_id,
            farmer_id=farmer_id,
            analysis_type="automatic_critical",
            trigger_context={
                "type": trigger_type,
                "current_conditions": telemetry_reading.dict(),
                "threshold_exceeded": get_exceeded_thresholds(telemetry_reading)
            }
        )
        
        # Create alert with AI recommendation summary
        await create_ai_recommendation_alert(
            farmer_id=farmer_id,
            device_id=device_id,
            recommendations=recommendations,
            trigger_context=trigger_context
        )
        
        # Update device last analysis timestamp
        await update_device_last_analysis(device_id)
        
    except asyncio.TimeoutError:
        logger.error(f"Auto-analysis timeout for device {device_id}")
        # Create fallback alert without AI recommendations
        await create_threshold_alert_only(farmer_id, device_id, telemetry_reading)
```

### Background Job Integration Pattern
```python
# Add to main FastAPI app
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(
        periodic_optimization_analysis,
        trigger=CronTrigger(hour=2, minute=0),  # Daily at 2 AM
        id="daily_ai_analysis",
        replace_existing=True
    )
    scheduler.start()

async def periodic_optimization_analysis():
    """Perform periodic AI analysis for devices without critical conditions"""
    
    # Get all devices due for periodic analysis
    devices = await get_devices_due_for_periodic_analysis()
    
    for device in devices:
        if device.auto_analysis_enabled:
            await handle_automatic_analysis_trigger(
                device_id=device.device_id,
                farmer_id=device.farmer_id,
                telemetry_reading=await get_latest_telemetry(device.device_id),
                trigger_type="automatic_periodic"
            )
```

### File Structure Requirements
```
backend/app/api/routes/
  └── katara.py              # Add auto-analysis endpoints and enhance telemetry

backend/app/services/
  └── ai_service.py          # Reuse from story 3-5, add auto-analysis context
  └── alert_service.py       # Reuse from story 3-8, add AI alert integration
  └── analysis_scheduler.py  # New: background job management
  └── device_settings.py    # New: device preference management

backend/app/models/
  └── schemas.py             # Add AutoAnalysisSettings, AnalysisTrigger models

backend/app/utils/
  └── rate_limiter.py        # New: intelligent analysis frequency control
  └── condition_analyzer.py # New: threshold detection and change analysis

backend/tests/
  └── test_auto_ai_analysis.py  # Comprehensive automatic analysis tests
```

### Integration Points with Existing Stories
- **Story 3-5 (AI Recommendations):** Reuse Claude API integration and recommendation storage
- **Story 3-8 (Alert System):** Integrate with alert creation and real-time notifications
- **Story 3-2 (Telemetry Ingestion):** Enhance existing endpoint with auto-analysis triggers
- **Story 3-6 (Weather Data):** Include weather context in automatic analysis
- **Story 3-7 (NDVI Imagery):** Include satellite data context when available

---

## Testing Requirements

### Unit Tests
- Automatic analysis trigger logic and threshold detection
- Rate limiting and frequency control algorithms
- Condition change analysis and significance detection
- Device preference management and settings validation
- Background job scheduling and execution

### Integration Tests
- Complete automatic analysis flow from telemetry to AI recommendation
- Alert integration with AI-generated recommendations
- Background job execution with multiple devices
- Error handling for AI API timeouts and failures
- Real-time notification delivery for automatic recommendations

### Performance Tests
- Concurrent automatic analysis for multiple devices
- Rate limiting under high telemetry volume
- Background job performance with large device pools
- Memory usage during peak automatic analysis periods

### Test Coverage
```python
async def test_automatic_analysis_on_critical_threshold():
    # Test automatic AI analysis trigger on critical conditions
    
async def test_periodic_optimization_analysis():
    # Test daily background analysis for non-critical conditions
    
async def test_rate_limiting_prevents_analysis_spam():
    # Test intelligent frequency control
    
async def test_farmer_preferences_respected():
    # Test device settings and auto-analysis enable/disable
    
async def test_condition_change_detection():
    # Test significant condition change detection logic
```

---

## Implementation Notes

### Previous Story Intelligence
- Build on AI service patterns from story 3-5
- Integrate with alert system from story 3-8
- Follow telemetry handling from story 3-2
- Use same authentication and authorization patterns
- Maintain consistent error handling and logging

### Critical Success Factors
- **Intelligent Triggering:** Avoid analysis spam while ensuring responsiveness
- **Context Enrichment:** Include all available environmental data
- **Farmer Control:** Allow users to customize automatic analysis behavior
- **Performance:** Handle automatic analysis at scale without blocking telemetry ingestion
- **Reliability:** Graceful fallback when AI API is unavailable

### Monitoring and Observability
- Track automatic analysis frequency and success rates
- Monitor AI API response times and timeout rates
- Alert on automatic analysis failures or rate limiting issues
- Measure farmer engagement with automatic recommendations

---

## Story Completion Status

**Status:** ready-for-dev  
**Epic Progress:** Epic 3 - 8/11 stories completed, 3 in progress  
**Dependencies:** Stories 3-2, 3-5, 3-8 must be completed first  
**Implementation Priority:** High - Core KATARA functionality  
**Estimated Effort:** 3-4 days  

**Next Steps:**
1. Implement automatic analysis trigger logic in telemetry endpoint
2. Create background job for periodic optimization analysis  
3. Add device preference management endpoints
4. Integrate AI recommendations with alert system
5. Implement intelligent rate limiting and frequency control
6. Add comprehensive test coverage
7. Update frontend to display automatic recommendations
8. Monitor performance and optimize as needed
