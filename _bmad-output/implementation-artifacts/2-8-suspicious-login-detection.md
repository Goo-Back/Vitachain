# Story: 2-8 Suspicious Login Detection

**Epic**: 2 - User Authentication & Profiles  
**Story ID**: 2.8  
**Status**: ready-for-dev  
**Priority**: P2 (Post-MVD)  
**Estimated Effort**: 3-5 days  

## User Story

**As a** platform administrator  
**I want** to detect and respond to suspicious login activities  
**So that** I can protect user accounts from unauthorized access and potential security breaches  

## Acceptance Criteria (BDD Format)

```gherkin
Feature: Suspicious Login Detection
  As a platform administrator
  I want to detect and respond to suspicious login activities
  So that I can protect user accounts from unauthorized access

  Scenario: Detect multiple failed login attempts from same IP
    Given a user has 5+ failed login attempts within 15 minutes from the same IP
    When the security monitor analyzes the login attempts
    Then the IP should be flagged as suspicious
    And an alert should be generated
    And the IP should be temporarily blocked for 1 hour

  Scenario: Detect login attempts from unusual geographic location
    Given a user typically logs in from Morocco
    When a login attempt occurs from a different country within 24 hours
    Then the location anomaly should be detected
    And a "was this you?" notification should be sent to the user
    And additional verification should be required

  Scenario: Detect rapid successive login attempts for different accounts
    Given an IP makes login attempts for 10+ different accounts within 5 minutes
    When the security monitor analyzes the pattern
    Then this should be flagged as potential credential stuffing
    And the IP should be blocked immediately
    And an admin alert should be sent

  Scenario: Detect login attempts from new device/browser
    Given a user has established login patterns
    When a login occurs from a completely new device/browser combination
    Then the new device should be flagged
    And the user should receive a new device notification
    And the login should be allowed with additional verification

  Scenario: Monitor login velocity anomalies
    Given a user's normal login frequency is 1-2 times per day
    When the user attempts to login 10+ times within 1 hour
    Then this velocity anomaly should be detected
    And the user should be notified of unusual activity
    And temporary rate limiting should be applied

  Scenario: Admin dashboard for security monitoring
    Given an administrator accesses the security dashboard
    When viewing the security metrics
    Then they should see real-time suspicious activity alerts
    And they should be able to view detailed IP reputation data
    And they should be able to manually block/unblock IPs
    And they should see historical security event trends
```

## Technical Requirements

### Core Functionality
- **Anomaly Detection Engine**: Extend existing `SecurityMonitor` class with advanced pattern recognition
- **Geographic Analysis**: IP geolocation lookup for unusual location detection
- **Device Fingerprinting**: Browser/device pattern analysis and tracking
- **Velocity Monitoring**: Login frequency and pattern analysis
- **Real-time Alerting**: Immediate notification system for suspicious activities
- **Admin Interface**: Security dashboard for monitoring and intervention

### Database Schema Extensions

```sql
-- Create security_events table for detailed tracking
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL, -- 'failed_login', 'location_anomaly', 'device_anomaly', 'velocity_anomaly'
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    user_agent TEXT,
    device_fingerprint TEXT,
    location_country VARCHAR(2), -- ISO country code
    location_city VARCHAR(100),
    metadata JSONB, -- Additional event-specific data
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES profiles(id),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create ip_reputation table for tracking IP behavior
CREATE TABLE IF NOT EXISTS ip_reputation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip_address INET UNIQUE NOT NULL,
    reputation_score INTEGER DEFAULT 100 CHECK (reputation_score >= 0 AND reputation_score <= 100),
    failed_attempts INTEGER DEFAULT 0,
    successful_logins INTEGER DEFAULT 0,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_until TIMESTAMPTZ,
    block_reason TEXT,
    metadata JSONB, -- Geographic data, ASN, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_login_patterns table for baseline behavior
CREATE TABLE IF NOT EXISTS user_login_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE UNIQUE,
    typical_ip_addresses INET[],
    typical_countries VARCHAR(2)[],
    typical_devices JSONB, -- Array of device fingerprints
    login_frequency_avg FLOAT DEFAULT 0, -- Average logins per day
    typical_login_hours INTEGER[], -- Hours when user typically logs in
    last_pattern_update TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create security_alerts table for active notifications
CREATE TABLE IF NOT EXISTS security_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    ip_address INET,
    requires_action BOOLEAN DEFAULT TRUE,
    action_taken TEXT,
    action_taken_by UUID REFERENCES profiles(id),
    action_taken_at TIMESTAMPTZ,
    is_read BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_ip_address ON security_events(ip_address);
CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON security_events(created_at);
CREATE INDEX IF NOT EXISTS idx_security_events_event_type ON security_events(event_type);

CREATE INDEX IF NOT EXISTS idx_ip_reputation_ip_address ON ip_reputation(ip_address);
CREATE INDEX IF NOT EXISTS idx_ip_reputation_reputation_score ON ip_reputation(reputation_score);
CREATE INDEX IF NOT EXISTS idx_ip_reputation_is_blocked ON ip_reputation(is_blocked);

CREATE INDEX IF NOT EXISTS idx_user_login_patterns_user_id ON user_login_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_security_alerts_user_id ON security_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_security_alerts_requires_action ON security_alerts(requires_action);
CREATE INDEX IF NOT EXISTS idx_security_alerts_created_at ON security_alerts(created_at);
```

### API Endpoints

```python
# New endpoints to add to auth.py or create security.py router

@router.post("/security/analyze-login")
async def analyze_login_attempt(
    request: LoginAnalysisRequest,
    http_request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Analyze login attempt for suspicious patterns
    Called during login process before authentication succeeds
    """

@router.get("/security/dashboard/metrics")
async def get_security_metrics(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get security metrics for admin dashboard
    Requires ADMIN role
    """

@router.get("/security/alerts")
async def get_security_alerts(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get security alerts for admin or user
    Filtered by user role
    """

@router.post("/security/alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: str,
    resolution: AlertResolutionRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Resolve a security alert with action taken
    Requires ADMIN role
    """

@router.post("/security/ip/{ip_address}/block")
async def block_ip_address(
    ip_address: str,
    block_request: IPBlockRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Manually block an IP address
    Requires ADMIN role
    """

@router.get("/security/ip/{ip_address}/reputation")
async def get_ip_reputation(
    ip_address: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get detailed reputation data for IP address
    Requires ADMIN role
    """
```

## Architecture Compliance

### Integration with Existing Systems
- **Extend SecurityMonitor**: Enhance existing `security_monitoring.py` with new detection algorithms
- **Supabase Integration**: Use existing Supabase client and RLS policies
- **Logging Integration**: Leverage existing structured logging with `structlog`
- **Rate Limiting**: Integrate with existing rate limiting infrastructure in `auth.py`

### Code Structure Requirements
```
backend/app/core/
├── security_monitoring.py (extend existing)
├── security_analytics.py (new)
├── geo_ip_service.py (new)
└── device_fingerprinting.py (new)

backend/app/api/routes/
├── auth.py (extend existing)
└── security.py (new)

backend/app/models/
├── security_schemas.py (new)
└── security_models.py (new)

backend/app/services/
├── security_service.py (new)
└── notification_service.py (extend existing)
```

### Security Requirements
- **Performance**: All analysis must complete within 200ms to not impact login experience
- **Privacy**: Store only necessary data, comply with GDPR requirements
- **False Positives**: Minimize false positive rate below 5%
- **Scalability**: Handle 1000+ concurrent login analysis requests
- **Data Retention**: Keep security events for 90 days, then archive

## Implementation Tasks

### Phase 1: Core Detection Engine (2-3 days)
1. **Extend SecurityMonitor Class**
   - Add geographic anomaly detection
   - Add device fingerprinting analysis
   - Add velocity pattern detection
   - Add credential stuffing detection

2. **Database Migration**
   - Create new security tables
   - Add RLS policies for security data
   - Create necessary indexes
   - Add triggers for automatic updates

3. **IP Geolocation Service**
   - Implement IP geolocation lookup
   - Cache location data for performance
   - Handle privacy-compliant location storage

### Phase 2: API Integration (1-2 days)
1. **Security API Endpoints**
   - Implement login analysis endpoint
   - Create admin security dashboard APIs
   - Add alert management endpoints

2. **Integration with Auth Flow**
   - Modify login endpoint to call security analysis
   - Add "was this you?" notification flow
   - Implement additional verification challenges

### Phase 3: Dashboard & Notifications (1 day)
1. **Admin Dashboard Components**
   - Security metrics overview
   - Real-time alert feed
   - IP reputation management
   - Historical trend analysis

2. **Notification System**
   - Email alerts for suspicious activity
   - In-app notifications for users
   - Admin escalation workflows

## Testing Requirements

### Unit Tests
- Test all detection algorithms with various scenarios
- Test database schema and RLS policies
- Test API endpoints with different user roles
- Test performance under load

### Integration Tests
- Test integration with existing auth flow
- Test end-to-end suspicious login detection
- Test notification delivery
- Test admin dashboard functionality

### Security Tests
- Test with various attack patterns
- Test false positive minimization
- Test data privacy compliance
- Test rate limiting effectiveness

## Previous Story Intelligence

### From Story 2-7 (Admin User Management Dashboard)
- **Admin Authentication**: Use existing admin authentication patterns
- **RLS Policies**: Follow established Row Level Security patterns
- **Dashboard Structure**: Consistent with existing admin interface patterns
- **Notification System**: Leverage existing email service infrastructure

### From Story 2-6 (Role-Based Access Control)
- **Authorization**: Use existing JWT role extraction patterns
- **Permission Checks**: Follow established role validation patterns
- **Admin-only Features**: Use existing admin role checks

## Latest Technical Information (2024 Best Practices)

### Anomaly Detection Patterns
Based on 2024 security research, implement these detection patterns:

1. **Geographic Anomalies**
   - Login from different country within 24 hours
   - Impossible travel time between locations
   - Login from high-risk countries

2. **Device/Behavioral Anomalies**
   - New browser/device combination
   - Unusual login time patterns
   - Rapid password changes

3. **Velocity-Based Detection**
   - Multiple failed attempts in short time
   - Credential stuffing patterns
   - Brute force attack detection

4. **Reputation-Based Analysis**
   - IP reputation scoring
   - Historical behavior analysis
   - Threat intelligence integration

### Modern Security Approaches
- **Machine Learning**: Consider ML models for pattern recognition (future enhancement)
- **Real-time Processing**: Sub-200ms analysis time requirement
- **Privacy-First**: GDPR-compliant data minimization
- **Adaptive Thresholds**: Dynamic thresholds based on user behavior

## Project Context Reference

### Technology Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: Supabase PostgreSQL with RLS
- **Authentication**: Supabase Auth with JWT
- **Logging**: Structured logging with `structlog`
- **Rate Limiting**: Existing in-memory rate limiting

### Key Dependencies
- `supabase-py`: For database operations
- `httpx`: For external API calls (geolocation)
- `python-jose`: For JWT validation
- `structlog`: For structured logging
- `fastapi`: For API endpoints

### Environment Variables Required
```bash
# Existing variables (reuse)
SUPABASE_URL
SUPABASE_SERVICE_KEY
SUPABASE_JWT_SECRET

# New variables for this story
IPGEOLOCATION_API_KEY  # For IP geolocation service
SECURITY_ALERT_EMAIL   # Admin notification email
SECURITY_WEBHOOK_URL   # Optional webhook for alerts
```

## Success Criteria

### Functional Success
- [ ] Detect 95% of suspicious login patterns
- [ ] False positive rate below 5%
- [ ] Admin dashboard displays real-time metrics
- [ ] Users receive "was this you?" notifications for anomalies
- [ ] Automatic IP blocking for high-confidence threats

### Performance Success
- [ ] Login analysis completes within 200ms
- [ ] Dashboard loads within 2 seconds
- [ ] System handles 1000+ concurrent analyses
- [ ] Database queries optimized with proper indexing

### Security Success
- [ ] All security data protected by RLS
- [ ] GDPR-compliant data handling
- [ ] No sensitive data in logs
- [ ] Proper audit trail for all security actions

## Risk Mitigation

### Technical Risks
- **Performance Impact**: Mitigate with efficient algorithms and caching
- **False Positives**: Implement tunable thresholds and manual review
- **Privacy Concerns**: Minimize data collection and ensure GDPR compliance
- **Complexity**: Phase implementation and reuse existing patterns

### Operational Risks
- **Alert Fatigue**: Implement smart alert grouping and prioritization
- **User Friction**: Use progressive verification, not blocking by default
- **Maintenance**: Implement automated cleanup and monitoring

## Completion Status

**Status**: ready-for-dev  
**Completion Note**: Ultimate context engine analysis completed - comprehensive developer guide created with existing infrastructure integration, latest security best practices, and detailed implementation roadmap.
