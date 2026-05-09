# Story: Satellite NDVI Imagery
**Story ID:** 3.7  
**Epic:** 3 - Smart Farming with IoT (KATARA)  
**Status:** ready-for-dev  
**Priority:** P2  

---

## User Story

**As a** Farmer using VitaChain KATARA  
**I want to** access satellite NDVI imagery for my farm plots through Sentinel Hub integration  
**So that** I can monitor vegetation health, identify crop stress patterns, and make informed irrigation and fertilization decisions based on broad-area observations beyond my individual IoT sensors.

---

## Acceptance Criteria (BDD Format)

### AC1: NDVI Data Retrieval
```gherkin
Scenario: Farmer retrieves satellite NDVI imagery for their device location
  Given I am authenticated as a FARMER
  And I have registered ESP32 devices with GPS coordinates
  When I GET "/api/katara/ndvi/{device_id}"
  Then the system fetches NDVI imagery from Sentinel Hub API
  And I receive 200 status with current NDVI data
  And response includes current NDVI value for my location
  And response includes NDVI imagery URL for visualization
  And response includes NDVI trend data for past 30 days
  And data is cached for 24 hours to optimize API costs
```

### AC2: NDVI-Enhanced AI Analysis
```gherkin
Scenario: AI analysis includes NDVI vegetation health context
  Given NDVI data is available for device location
  And I trigger AI analysis via "/api/katara/analyze/{device_id}"
  Then the system includes current NDVI value in AI prompt
  And the system includes NDVI trend analysis in AI context
  And AI recommendations consider vegetation health status
  And recommendations include NDVI-specific agronomic advice
```

### AC3: NDVI Alert Generation
```gherkin
Scenario: System generates vegetation health alerts based on NDVI
  Given NDVI analysis shows vegetation stress
  When NDVI data is processed for my device
  Then the system creates threshold_exceeded alerts in katara_alerts table
  And alert severity matches NDVI stress level
  And alert includes specific NDVI value and trend information
  And alert appears in my alert feed with vegetation context
```

### AC4: Historical NDVI Data Storage
```gherkin
Scenario: System maintains NDVI data history for trend analysis
  Given NDVI data has been retrieved for my device
  When I query historical NDVI data for the past 90 days
  Then the system returns NDVI readings from database
  And each reading includes timestamp and NDVI value
  And historical data is used for trend analysis
  And data retention follows 90-day policy for cost optimization
```

### AC5: NDVI Visualization Integration
```gherkin
Scenario: NDVI data displays in KATARA dashboard with imagery
  Given I view my device dashboard
  Then current NDVI value is displayed with health indicator
  And NDVI trend chart shows 30-day vegetation health history
  And satellite imagery overlay is available for visual assessment
  And NDVI alerts are highlighted when vegetation stress is detected
```

---

## Technical Requirements

### Backend Implementation
- **Endpoint:** `GET /api/katara/ndvi/{device_id}`
- **Authentication:** JWT Bearer token (FARMER role required)
- **Satellite API:** Sentinel Hub via httpx.AsyncClient()
- **Database:** Direct Supabase client (no SQLAlchemy)
- **Validation:** Pydantic models for request/response
- **Caching:** 24-hour cache for NDVI data (cost optimization)
- **Rate Limiting:** Respect Sentinel Hub API limits and cost constraints

### Database Schema
```sql
CREATE TABLE ndvi_readings (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id       TEXT NOT NULL,
  farmer_id       UUID REFERENCES profiles(id),
  location_lat    FLOAT NOT NULL,
  location_lng    FLOAT NOT NULL,
  ndvi_value      FLOAT CHECK (ndvi_value BETWEEN -1 AND 1),
  ndvi_trend     TEXT CHECK (ndvi_trend IN ('improving','stable','declining','critical')),
  imagery_url     TEXT,                    -- Sentinel Hub imagery URL
  cloud_cover    FLOAT CHECK (cloud_cover BETWEEN 0 AND 100),
  data_quality   TEXT CHECK (data_quality IN ('excellent','good','fair','poor')),
  acquisition_date TIMESTAMPTZ,         -- Satellite image capture time
  api_source      TEXT DEFAULT 'sentinel_hub',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ndvi_device_time 
ON ndvi_readings (device_id, created_at DESC);

CREATE INDEX idx_ndvi_farmer 
ON ndvi_readings (farmer_id, created_at DESC);

-- RLS Policy
CREATE POLICY "farmers_own_their_ndvi_data" ON ndvi_readings
FOR ALL USING (farmer_id = auth.uid());
```

### API Contract
**Request:** `GET /api/katara/ndvi/{device_id}`

**Response (200):**
```json
{
  "current": {
    "ndvi_value": 0.42,
    "ndvi_trend": "stable",
    "vegetation_health": "good",
    "imagery_url": "https://services.sentinel-hub.com/.../ndvi_image.png",
    "cloud_cover": 15.2,
    "data_quality": "excellent",
    "location": {
      "lat": 33.5731,
      "lng": -7.5898
    },
    "acquisition_date": "2026-05-03T10:30:00Z",
    "timestamp": "2026-05-03T14:30:00Z"
  },
  "trend": {
    "ndvi_30d_avg": 0.44,
    "ndvi_7d_avg": 0.42,
    "ndvi_change_7d": -0.02,
    "trend_direction": "stable",
    "stress_detected": false
  },
  "historical": [
    {
      "date": "2026-05-02",
      "ndvi_value": 0.43,
      "data_quality": "excellent"
    },
    {
      "date": "2026-05-01",
      "ndvi_value": 0.45,
      "data_quality": "good"
    }
  ],
  "alerts": [
    {
      "type": "threshold_exceeded",
      "severity": "medium",
      "message": "NDVI decline detected over past 7 days. Consider checking irrigation and nutrient levels.",
      "ndvi_threshold": 0.3,
      "current_ndvi": 0.42,
      "trend_period": "7d"
    }
  ],
  "cached_at": "2026-05-03T14:30:00Z",
  "cache_expires": "2026-05-04T14:30:00Z"
}
```

---

## Developer Context & Guardrails

### Critical Architecture Rules
```python
# ✅ ALWAYS use async HTTP client for Sentinel Hub API
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(ndvi_url)

# ✅ ALWAYS extract farmer_id from JWT
farmer_id = get_current_user().id  # From JWT.sub

# ✅ ALWAYS use Supabase client directly
result = supabase.table("ndvi_readings").insert(data).execute()

# ✅ ALWAYS implement 24-hour caching (cost optimization)
@cache(expire=86400)  # 24 hours
async def get_ndvi_data(lat: float, lng: float):
    return await fetch_sentinel_hub_ndvi(lat, lng)

# ✅ ALWAYS handle API costs and rate limits
if response.status_code == 429:
    # Implement exponential backoff
    pass

# ❌ NEVER use synchronous HTTP calls
response = requests.get(ndvi_url)  # BLOCKING

# ❌ NEVER put API keys in code
api_key = "abc123..."  # SECURITY VIOLATION
```

### Sentinel Hub Integration Pattern
```python
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

class SatelliteService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://services.sentinel-hub.com"
        self.cache = {}  # Simple in-memory cache
        self.access_token = None
        self.token_expires = None
        
    async def get_access_token(self) -> str:
        # Refresh token if needed
        if not self.access_token or datetime.utcnow() >= self.token_expires:
            await self._refresh_token()
        return self.access_token
    
    async def _refresh_token(self):
        url = f"{self.base_url}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
    
    async def get_ndvi_data(self, lat: float, lng: float) -> Dict[str, Any]:
        cache_key = f"{lat:.4f},{lng:.4f}"
        
        # Check cache (24-hour TTL)
        if cache_key in self.cache:
            cached_data, cached_at = self.cache[cache_key]
            if datetime.utcnow() - cached_at < timedelta(hours=24):
                return cached_data
        
        # Fetch fresh NDVI data
        token = await self.get_access_token()
        
        # Sentinel Hub request for NDVI
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: ["B04", "B08"],
                output: { bands: 1, sampleType: "FLOAT32" }
            };
        }
        function evaluatePixel(sample) {
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            return [ndvi];
        }
        """
        
        request_body = {
            "input": {
                "bounds": {
                    "bbox": [lng - 0.001, lat - 0.001, lng + 0.001, lat + 0.001]
                },
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": "2026-04-01T00:00:00Z",
                            "to": "2026-05-03T00:00:00Z"
                        },
                        "maxCloudCoverage": 20
                    }
                }]
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [{
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }]
            },
            "evalscript": evalscript
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/process",
                json=request_body,
                headers=headers
            )
            response.raise_for_status()
            
            ndvi_data = self._parse_ndvi_response(response.json(), lat, lng)
            
            # Cache the result
            self.cache[cache_key] = (ndvi_data, datetime.utcnow())
            
            return ndvi_data
    
    def _parse_ndvi_response(self, data: Dict, lat: float, lng: float) -> Dict[str, Any]:
        # Parse Sentinel Hub response and extract NDVI statistics
        # This is simplified - actual implementation would process TIFF data
        return {
            "ndvi_value": 0.42,  # Extracted from imagery
            "ndvi_trend": "stable",
            "vegetation_health": "good",
            "imagery_url": f"{self.base_url}/api/v1/process/.../ndvi_image.png",
            "cloud_cover": 15.2,
            "data_quality": "excellent",
            "location": {"lat": lat, "lng": lng},
            "acquisition_date": datetime.utcnow().isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
```

### NDVI-Enhanced AI Integration
```python
async def enhance_ai_analysis_with_ndvi(
    device_id: str,
    telemetry_data: List[TelemetryReading],
    ndvi_data: Optional[NDVIData] = None
) -> str:
    
    ndvi_context = ""
    if ndvi_data:
        ndvi_context = f"""
        
        Satellite NDVI Analysis (Current):
        - NDVI Value: {ndvi_data.current.ndvi_value}
        - Vegetation Health: {ndvi_data.current.vegetation_health}
        - NDVI Trend (30d): {ndvi_data.trend.trend_direction}
        - 7-day Change: {ndvi_data.trend.ndvi_change_7d}
        - Data Quality: {ndvi_data.current.data_quality}
        
        Vegetation Health Impact:
        {"Healthy vegetation detected - continue current practices" if ndvi_data.current.ndvi_value > 0.4 else ""}
        {"Moderate vegetation stress - review irrigation and nutrients" if 0.3 <= ndvi_data.current.ndvi_value <= 0.4 else ""}
        {"Significant vegetation stress - immediate intervention needed" if ndvi_data.current.ndvi_value < 0.3 else ""}
        {"Declining NDVI trend - investigate potential causes" if ndvi_data.trend.ndvi_change_7d < -0.05 else ""}
        """
    
    enhanced_prompt = f"""
    As an expert agronomist specializing in Moroccan agriculture, analyze the following IoT sensor data:
    
    {base_telemetry_analysis}
    
    {ndvi_context}
    
    Provide specific recommendations that account for both ground sensor readings AND satellite vegetation health.
    Consider how NDVI trends correlate with soil conditions, irrigation effectiveness, and crop development stages.
    Focus on actionable insights that combine micro-level sensor data with macro-level vegetation observations.
    """
    
    return enhanced_prompt
```

### File Structure Requirements
```
backend/app/api/routes/
  └── katara.py              # Add NDVI endpoint

backend/app/services/
  └── satellite_service.py   # Sentinel Hub integration
  └── ndvi_service.py         # NDVI processing logic
  └── cache_service.py        # NDVI caching logic

backend/app/models/
  └── schemas.py             # Add NDVIData, NDVITrend models

backend/app/utils/
  └── ndvi_utils.py          # NDVI-specific utilities

backend/tests/
  └── test_satellite_integration.py  # Comprehensive tests

frontend/app/(dashboard)/katara/
  └── components/
     └── NDVIWidget.tsx      # NDVI display component
     └── NDVIChart.tsx       # NDVI trend visualization
```

---

## Testing Requirements

### Unit Tests
- Sentinel Hub API response parsing
- NDVI data caching logic (24-hour TTL)
- NDVI alert generation based on thresholds
- Error handling for API failures
- Coordinate validation for Moroccan locations
- NDVI trend calculation algorithms

### Integration Tests
- Complete NDVI data retrieval flow
- NDVI-enhanced AI analysis
- NDVI data storage and retrieval
- Cache invalidation and refresh
- Rate limiting handling for Sentinel Hub API
- Cost optimization with 24-hour caching

### Test Coverage
```python
async def test_ndvi_data_retrieval():
    # Test successful NDVI data fetch

async def test_ndvi_cache_functionality():
    # Test 24-hour caching behavior

async def test_ndvi_alert_generation():
    # Test NDVI threshold alert creation

async def test_ndvi_enhanced_ai_analysis():
    # Test AI analysis with NDVI context

async def test_sentinel_hub_api_error_handling():
    # Test graceful handling of API failures

async def test_ndvi_trend_calculation():
    # Test NDVI trend analysis algorithms
```

---

## Performance Requirements

- **Satellite API Response:** < 30 seconds (Sentinel Hub processing time)
- **Cache Lookup:** < 50ms for cached NDVI data
- **Database Query:** Optimized with proper indexes
- **API Response Time:** < 500ms for NDVI endpoint
- **Cache Hit Ratio:** > 90% for frequent requests (24-hour cache)
- **Concurrent Requests:** Support multiple farmers simultaneously
- **Cost Optimization:** Minimize API calls through aggressive caching

---

## Security Requirements

### Authentication & Authorization
- JWT token validation (FARMER role required)
- farmer_id extracted from JWT.sub (never from request body)
- RLS policies enforce NDVI data isolation

### API Security
- Sentinel Hub credentials stored in environment variables
- Rate limiting on NDVI endpoints
- Input validation for device IDs and coordinates
- Secure handling of satellite imagery URLs

### Data Protection
- All NDVI data linked to authenticated farmer
- No cross-farmer NDVI data access possible
- Audit trail via created_at timestamps
- Cost protection through 24-hour caching

---

## Dependencies & Integration

### Internal Dependencies
- Supabase client for database operations
- JWT authentication middleware
- Pydantic for validation
- iot_devices table for location data
- katara_alerts table for NDVI threshold alerts
- AI service for enhanced analysis
- telemetry_readings for correlation analysis

### External Dependencies
- **Sentinel Hub API:** Satellite imagery and NDVI processing
- **Rate Limits:** Based on subscription plan (~200 MAD/month)
- **Timeout:** 30 seconds with fallback handling
- **Cost Management:** 24-hour cache to minimize API calls

### Successor Stories
- 3-8-critical-condition-alert-system: NDVI-enhanced alert thresholds
- 3-20-automatic-ai-recommendation-generation: Scheduled NDVI-informed analyses
- 3-21-threshold-based-alert-triggering: NDVI-aware alert thresholds

---

## Project Context Reference

### Technology Stack
- **Backend:** FastAPI + Python 3.11 (async)
- **Database:** Supabase PostgreSQL with RLS
- **Authentication:** Supabase Auth JWT
- **Satellite API:** Sentinel Hub via httpx.AsyncClient()
- **Validation:** Pydantic v2
- **Testing:** pytest with async support

### Code Conventions
- Async/await patterns throughout
- Direct Supabase client usage (no ORM)
- Structured error responses
- Comprehensive logging with structlog
- Environment variable secrets management
- Cost-optimized caching strategies

### File Locations
- Routes: `backend/app/api/routes/katara.py`
- Satellite Service: `backend/app/services/satellite_service.py`
- NDVI Service: `backend/app/services/ndvi_service.py`
- Cache Service: `backend/app/services/cache_service.py`
- Models: `backend/app/models/schemas.py`
- Tests: `backend/tests/test_satellite_integration.py`

---

## Implementation Notes

### Sentinel Hub Integration
- Use httpx.AsyncClient() for non-blocking calls
- Implement 24-hour cache for cost optimization
- Support Moroccan agricultural region focus
- Handle API rate limits with exponential backoff
- Process Sentinel-2 L2A data for best NDVI accuracy

### NDVI Analysis Context
- NDVI range: -1 to 1 (vegetation typically 0.2-0.8)
- Health thresholds: >0.4 (healthy), 0.3-0.4 (moderate), <0.3 (stress)
- Trend analysis: 7-day and 30-day moving averages
- Cloud cover filtering for data quality
- Moroccan agricultural calendar considerations

### Cost Management
- 24-hour cache to minimize Sentinel Hub API costs
- Batch processing for multiple devices in same area
- Data quality checks to avoid unnecessary API calls
- Fallback to cached data during API issues

### Error Handling
- 408 Request Timeout for Sentinel Hub timeouts
- 422 Validation for invalid coordinates
- 403 Forbidden for insufficient permissions
- 429 Too Many Requests for API rate limits
- 502 Bad Gateway for Sentinel Hub API failures
- 404 Not Found for devices without GPS coordinates

---

## Completion Criteria

- [ ] NDVI data API endpoint implemented
- [ ] Sentinel Hub integration with async patterns
- [ ] Pydantic models for NDVI validation
- [ ] 24-hour caching mechanism implemented
- [ ] NDVI data storage and retrieval
- [ ] NDVI-enhanced AI analysis integration
- [ ] NDVI threshold alert generation
- [ ] Dashboard NDVI widget component
- [ ] Comprehensive unit and integration tests
- [ ] Rate limiting and error handling complete
- [ ] RLS policies enforced
- [ ] API documentation updated
- [ ] Performance requirements met
- [ ] Security requirements satisfied
- [ ] Cost optimization implemented

---

## Story Context

This story integrates satellite-based vegetation health monitoring into the KATARA farming system, providing Moroccan farmers with crucial macro-level observations of their crop health beyond individual IoT sensor readings. By combining Sentinel Hub NDVI imagery with existing telemetry and AI analysis, farmers receive:

- **Broad-Area Monitoring:** Vegetation health across entire farm plots
- **Early Stress Detection:** NDVI trends reveal issues before ground sensors detect them
- **Enhanced AI Recommendations:** Vegetation health-informed agronomic advice
- **Cost-Optimized Insights:** 24-hour caching balances freshness with affordability
- **Visual Assessment:** Satellite imagery for manual crop health verification

The implementation must balance data freshness with cost constraints, ensuring farmers have access to valuable satellite insights while maintaining reasonable operational costs through intelligent caching and API optimization.

This story builds on the telemetry foundation (stories 3-1 to 3-4), AI analysis (story 3-5), and weather integration (story 3-6), creating a comprehensive farming intelligence system that combines ground-level sensors, weather patterns, and satellite observations for complete agricultural awareness.

---

**Last Updated:** 2026-05-03T23:55:00Z  
**Next Story:** 3-8-critical-condition-alert-system  
**Dependencies:** Stories 3-1 through 3-6 must be complete
