-- Migration: Security Detection Tables
-- Description: Create tables for suspicious login detection and security monitoring
-- Version: 1.0
-- Date: 2026-05-02

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

-- RLS Policies for security_events
-- Only admins and the user themselves can see security events
CREATE POLICY "security_events_select_policy" ON security_events
    FOR SELECT
    USING (
        auth.uid() = user_id OR 
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role = 'ADMIN'
        )
    );

CREATE POLICY "security_events_insert_policy" ON security_events
    FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = auth.uid() 
        AND role = 'ADMIN'
    ));

-- RLS Policies for ip_reputation
-- Only admins can see IP reputation data
CREATE POLICY "ip_reputation_select_policy" ON ip_reputation
    FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = auth.uid() 
        AND role = 'ADMIN'
    ));

CREATE POLICY "ip_reputation_update_policy" ON ip_reputation
    FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = auth.uid() 
        AND role = 'ADMIN'
    ));

-- RLS Policies for user_login_patterns
-- Only admins and the user themselves can see login patterns
CREATE POLICY "user_login_patterns_select_policy" ON user_login_patterns
    FOR SELECT
    USING (
        auth.uid() = user_id OR 
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role = 'ADMIN'
        )
    );

CREATE POLICY "user_login_patterns_update_policy" ON user_login_patterns
    FOR UPDATE
    USING (auth.uid() = user_id);

-- RLS Policies for security_alerts
-- Only admins and the user themselves can see security alerts
CREATE POLICY "security_alerts_select_policy" ON security_alerts
    FOR SELECT
    USING (
        auth.uid() = user_id OR 
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role = 'ADMIN'
        )
    );

CREATE POLICY "security_alerts_update_policy" ON security_alerts
    FOR UPDATE
    USING (
        auth.uid() = user_id OR 
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role = 'ADMIN'
        )
    );

-- Enable RLS on security tables
ALTER TABLE security_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ip_reputation ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_login_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_alerts ENABLE ROW LEVEL SECURITY;

-- Grant necessary permissions
GRANT ALL ON security_events TO authenticated;
GRANT ALL ON ip_reputation TO authenticated;
GRANT ALL ON user_login_patterns TO authenticated;
GRANT ALL ON security_alerts TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE security_events IS 'Security events table for tracking suspicious login activities and anomalies';
COMMENT ON COLUMN security_events.id IS 'Unique identifier for each security event';
COMMENT ON COLUMN security_events.event_type IS 'Type of security event (failed_login, location_anomaly, device_anomaly, velocity_anomaly)';
COMMENT ON COLUMN security_events.severity IS 'Severity level of the security event';
COMMENT ON COLUMN security_events.user_id IS 'User ID associated with the security event';
COMMENT ON COLUMN security_events.ip_address IS 'IP address from which the event originated';
COMMENT ON COLUMN security_events.user_agent IS 'User agent string of the browser/client';
COMMENT ON COLUMN security_events.device_fingerprint IS 'Device fingerprint for device tracking';
COMMENT ON COLUMN security_events.location_country IS 'Country code where the login originated';
COMMENT ON COLUMN security_events.location_city IS 'City where the login originated';
COMMENT ON COLUMN security_events.metadata IS 'Additional event-specific data in JSON format';
COMMENT ON COLUMN security_events.is_resolved IS 'Whether the security event has been resolved';
COMMENT ON COLUMN security_events.resolved_by IS 'Admin who resolved the security event';
COMMENT ON COLUMN security_events.resolved_at IS 'Timestamp when the security event was resolved';
COMMENT ON COLUMN security_events.created_at IS 'Timestamp when the security event was created';
COMMENT ON COLUMN security_events.updated_at IS 'Timestamp when the security event was last updated';

COMMENT ON TABLE ip_reputation IS 'IP reputation tracking table for monitoring IP behavior and trustworthiness';
COMMENT ON COLUMN ip_reputation.ip_address IS 'IP address being tracked';
COMMENT ON COLUMN ip_reputation.reputation_score IS 'Reputation score from 0-100 (higher is better)';
COMMENT ON COLUMN ip_reputation.failed_attempts IS 'Count of failed authentication attempts';
COMMENT ON COLUMN ip_reputation.successful_logins IS 'Count of successful logins';
COMMENT ON COLUMN ip_reputation.last_activity IS 'Timestamp of last activity from this IP';
COMMENT ON COLUMN ip_reputation.is_blocked IS 'Whether the IP address is currently blocked';
COMMENT ON COLUMN ip_reputation.blocked_until IS 'Timestamp until which the IP is blocked';
COMMENT ON COLUMN ip_reputation.block_reason IS 'Reason for blocking the IP address';
COMMENT ON COLUMN ip_reputation.metadata IS 'Additional IP data in JSON format (geographic, ASN, etc.)';
COMMENT ON COLUMN ip_reputation.created_at IS 'Timestamp when the IP reputation record was created';
COMMENT ON COLUMN ip_reputation.updated_at IS 'Timestamp when the IP reputation record was last updated';

COMMENT ON TABLE user_login_patterns IS 'User login behavior patterns for baseline comparison and anomaly detection';
COMMENT ON COLUMN user_login_patterns.user_id IS 'User ID whose login patterns are being tracked';
COMMENT ON COLUMN user_login_patterns.typical_ip_addresses IS 'Array of typical IP addresses for this user';
COMMENT ON COLUMN user_login_patterns.typical_countries IS 'Array of typical country codes for this user';
COMMENT ON COLUMN user_login_patterns.typical_devices IS 'Array of typical device fingerprints for this user';
COMMENT ON COLUMN user_login_patterns.login_frequency_avg IS 'Average login frequency per day for this user';
COMMENT ON COLUMN user_login_patterns.typical_login_hours IS 'Array of typical hours when user logs in';
COMMENT ON COLUMN user_login_patterns.last_pattern_update IS 'Timestamp when user patterns were last updated';
COMMENT ON COLUMN user_login_patterns.created_at IS 'Timestamp when user login patterns were first recorded';
COMMENT ON COLUMN user_login_patterns.updated_at IS 'Timestamp when user login patterns were last updated';

COMMENT ON TABLE security_alerts IS 'Security alerts table for active notifications and admin actions';
COMMENT ON COLUMN security_alerts.alert_type IS 'Type of security alert';
COMMENT ON COLUMN security_alerts.severity IS 'Severity level of the alert';
COMMENT ON COLUMN security_alerts.title IS 'Title of the security alert';
COMMENT ON COLUMN security_alerts.description IS 'Detailed description of the security alert';
COMMENT ON COLUMN security_alerts.user_id IS 'User ID associated with the alert';
COMMENT ON COLUMN security_alerts.ip_address IS 'IP address associated with the alert';
COMMENT ON COLUMN security_alerts.requires_action IS 'Whether the alert requires admin action';
COMMENT ON COLUMN security_alerts.action_taken IS 'Action taken to resolve the alert';
COMMENT ON COLUMN security_alerts.action_taken_by IS 'Admin who took the action';
COMMENT ON COLUMN security_alerts.action_taken_at IS 'Timestamp when action was taken';
COMMENT ON COLUMN security_alerts.is_read IS 'Whether the alert has been read';
COMMENT ON COLUMN security_alerts.metadata IS 'Additional alert data in JSON format';
COMMENT ON COLUMN security_alerts.created_at IS 'Timestamp when the alert was created';
COMMENT ON COLUMN security_alerts.updated_at IS 'Timestamp when the alert was last updated';

-- Create trigger for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_security_events_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION update_ip_reputation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION update_user_login_patterns_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION update_security_alerts_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER security_events_updated_at_trigger
    BEFORE UPDATE ON security_events
    FOR EACH ROW
    EXECUTE FUNCTION update_security_events_timestamp();

CREATE TRIGGER ip_reputation_updated_at_trigger
    BEFORE UPDATE ON ip_reputation
    FOR EACH ROW
    EXECUTE FUNCTION update_ip_reputation_timestamp();

CREATE TRIGGER user_login_patterns_updated_at_trigger
    BEFORE UPDATE ON user_login_patterns
    FOR EACH ROW
    EXECUTE FUNCTION update_user_login_patterns_timestamp();

CREATE TRIGGER security_alerts_updated_at_trigger
    BEFORE UPDATE ON security_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_security_alerts_timestamp();
