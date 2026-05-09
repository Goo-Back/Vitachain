-- Migration: Admin Audit Logs Table
-- Description: Create table for logging all admin actions for audit trail and compliance
-- Version: 1.0
-- Date: 2026-05-02

-- Create admin_audit_logs table
CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    target_user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    target_user_email VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    reason TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_admin_id ON admin_audit_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_target_user_id ON admin_audit_logs(target_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_action ON admin_audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_created_at ON admin_audit_logs(created_at);

-- Create RLS (Row Level Security) policies
-- Only admins can see audit logs
CREATE POLICY "admin_audit_logs_select_policy" ON admin_audit_logs
    FOR SELECT
    USING (auth.uid() = admin_id)
    WITH CHECK (EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = auth.uid() 
        AND role = 'ADMIN'
    ));

-- Only admins can insert audit logs
CREATE POLICY "admin_audit_logs_insert_policy" ON admin_audit_logs
    FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = auth.uid() 
        AND role = 'ADMIN'
    ));

-- Enable RLS on the table
ALTER TABLE admin_audit_logs ENABLE ROW LEVEL SECURITY;

-- Create a function to automatically log admin actions
CREATE OR REPLACE FUNCTION log_admin_action(
    p_admin_id UUID,
    p_target_user_id UUID,
    p_action VARCHAR(50),
    p_old_value JSONB DEFAULT NULL,
    p_new_value JSONB DEFAULT NULL,
    p_reason TEXT DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO admin_audit_logs (
        admin_id = p_admin_id,
        target_user_id = p_target_user_id,
        action = p_action,
        old_value = p_old_value,
        new_value = p_new_value,
        reason = p_reason,
        ip_address = p_ip_address,
        user_agent = p_user_agent
    )
    RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT ALL ON admin_audit_logs TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT EXECUTE ON FUNCTION log_admin_action TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE admin_audit_logs IS 'Audit log table for tracking all admin actions including user management, role changes, and system modifications';
COMMENT ON COLUMN admin_audit_logs.id IS 'Unique identifier for each audit log entry';
COMMENT ON COLUMN admin_audit_logs.admin_id IS 'ID of the admin who performed the action';
COMMENT ON COLUMN admin_audit_logs.target_user_id IS 'ID of the user who was the target of the admin action';
COMMENT ON COLUMN admin_audit_logs.target_user_email IS 'Email of the target user (denormalized for easier searching)';
COMMENT ON COLUMN admin_audit_logs.action IS 'Type of action performed (e.g., update_status, update_role, bulk_update)';
COMMENT ON COLUMN admin_audit_logs.old_value IS 'Previous value before the action (JSON format for complex data)';
COMMENT ON COLUMN admin_audit_logs.new_value IS 'New value after the action (JSON format for complex data)';
COMMENT ON COLUMN admin_audit_logs.reason IS 'Reason provided by admin for the action';
COMMENT ON COLUMN admin_audit_logs.ip_address IS 'IP address from which the admin performed the action';
COMMENT ON COLUMN admin_audit_logs.user_agent IS 'User agent string of the admin browser/client';
COMMENT ON COLUMN admin_audit_logs.created_at IS 'Timestamp when the audit log entry was created';
COMMENT ON COLUMN admin_audit_logs.updated_at IS 'Timestamp when the audit log entry was last updated';

-- Create trigger for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_admin_audit_log_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER admin_audit_logs_updated_at_trigger
    BEFORE UPDATE ON admin_audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_admin_audit_log_timestamp();
