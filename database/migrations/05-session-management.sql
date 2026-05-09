-- Migration 05: Session Management for Logout and Session Invalidation
-- This migration adds user_sessions table for tracking active sessions
-- and implementing secure logout functionality with multi-device support

-- Create session tracking table for active session management
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    session_id TEXT UNIQUE NOT NULL,  -- JWT jti claim
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    logout_reason TEXT,
    logged_out_at TIMESTAMPTZ,
    logged_out_by UUID REFERENCES profiles(id),  -- For admin force logout
    force_logout BOOLEAN DEFAULT FALSE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_active ON user_sessions(user_id, is_active);

-- RLS Policies for user_sessions
-- Enable Row Level Security
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Policy for users to read their own sessions
CREATE POLICY "users_read_own_sessions" ON user_sessions FOR SELECT
  USING (user_id = auth.uid() OR auth.jwt()->>'role' = 'ADMIN');

-- Policy for service role and admin to manage sessions
CREATE POLICY "service_manage_sessions" ON user_sessions FOR ALL
  USING (auth.jwt()->>'role' = 'ADMIN' OR auth.jwt()->>'role' = 'service_role');

-- Function to automatically clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    UPDATE user_sessions 
    SET is_active = FALSE, 
        logged_out_at = NOW(),
        logout_reason = 'session_expired'
    WHERE is_active = TRUE 
    AND expires_at < NOW();
    
    -- Delete sessions expired more than 7 days ago
    DELETE FROM user_sessions 
    WHERE expires_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a trigger to automatically clean up expired sessions
-- Note: This would be called by a background job
-- CREATE OR REPLACE FUNCTION trigger_cleanup_sessions()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     PERFORM cleanup_expired_sessions();
--     RETURN NULL;
-- END;
-- $$ LANGUAGE plpgsql;

-- Add comment for documentation
COMMENT ON TABLE user_sessions IS 'Tracks active user sessions for secure logout and session management';
COMMENT ON COLUMN user_sessions.session_id IS 'JWT jti claim for unique session identification';
COMMENT ON COLUMN user_sessions.device_info IS 'JSON containing device fingerprint and details';
COMMENT ON COLUMN user_sessions.ip_address IS 'IP address of session creation';
COMMENT ON COLUMN user_sessions.user_agent IS 'Browser/user agent string';
COMMENT ON COLUMN user_sessions.expires_at IS 'Session expiration timestamp';
COMMENT ON COLUMN user_sessions.is_active IS 'Whether session is currently active';
COMMENT ON COLUMN user_sessions.logout_reason IS 'Reason for session logout (user_initiated, admin_force, session_expired)';
COMMENT ON COLUMN user_sessions.logged_out_by IS 'Admin user ID who forced logout, if applicable';
COMMENT ON COLUMN user_sessions.force_logout IS 'True if session was terminated by admin';
