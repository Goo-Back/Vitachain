-- Migration for Temporary Account Blocking Feature
-- Adds blocking functionality to user accounts with audit trail

-- Add blocking status to profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) 
  DEFAULT 'active' CHECK (account_status IN ('active', 'blocked', 'suspended'));

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS block_reason TEXT;

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS blocked_at TIMESTAMPTZ;

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS blocked_until TIMESTAMPTZ;

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS blocked_by UUID REFERENCES profiles(id);

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS auto_block BOOLEAN DEFAULT FALSE;

-- Create account_blocks table for detailed tracking
CREATE TABLE IF NOT EXISTS account_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    blocked_by UUID REFERENCES profiles(id),
    block_reason TEXT NOT NULL,
    block_duration_hours INTEGER NOT NULL,
    blocked_at TIMESTAMPTZ DEFAULT NOW(),
    blocked_until TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    auto_block BOOLEAN DEFAULT FALSE,
    security_event_id UUID REFERENCES security_events(id),
    unblocked_at TIMESTAMPTZ,
    unblocked_by UUID REFERENCES profiles(id),
    unblock_reason TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiles_account_status ON profiles(account_status);
CREATE INDEX IF NOT EXISTS idx_profiles_blocked_until ON profiles(blocked_until) WHERE blocked_until IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_account_blocks_user_id ON account_blocks(user_id);
CREATE INDEX IF NOT EXISTS idx_account_blocks_is_active ON account_blocks(is_active);
CREATE INDEX IF NOT EXISTS idx_account_blocks_blocked_until ON account_blocks(blocked_until);

-- Create function to automatically update account status
CREATE OR REPLACE FUNCTION update_account_block_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Update profiles.account_status based on blocked_until
    IF NEW.blocked_until IS NOT NULL AND NEW.blocked_until > NOW() THEN
        UPDATE profiles 
        SET account_status = 'blocked',
            block_reason = NEW.block_reason,
            blocked_at = NEW.blocked_at,
            blocked_until = NEW.blocked_until,
            blocked_by = NEW.blocked_by,
            auto_block = NEW.auto_block,
            updated_at = NOW()
        WHERE id = NEW.user_id;
    ELSIF NEW.blocked_until IS NULL OR NEW.blocked_until <= NOW() THEN
        UPDATE profiles 
        SET account_status = 'active',
            block_reason = NULL,
            blocked_at = NULL,
            blocked_until = NULL,
            blocked_by = NULL,
            auto_block = FALSE,
            updated_at = NOW()
        WHERE id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically update account status
CREATE TRIGGER trigger_update_account_block_status
    AFTER INSERT OR UPDATE ON account_blocks
    FOR EACH ROW
    EXECUTE FUNCTION update_account_block_status();

-- RLS Policies for account_blocks
ALTER TABLE account_blocks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_reads_all_blocks" ON account_blocks FOR SELECT
  USING (auth.jwt()->>'role' = 'ADMIN');

CREATE POLICY "admin_manages_blocks" ON account_blocks FOR ALL
  USING (auth.jwt()->>'role' = 'ADMIN')
  WITH CHECK (auth.jwt()->>'role' = 'ADMIN');

-- Function to clean up expired blocks
CREATE OR REPLACE FUNCTION cleanup_expired_blocks()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    -- Update expired blocks
    UPDATE account_blocks 
    SET is_active = FALSE,
        unblocked_at = NOW(),
        unblock_reason = 'Automatic expiration'
    WHERE is_active = TRUE 
      AND blocked_until <= NOW();
    
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    
    -- Update corresponding profiles
    UPDATE profiles 
    SET account_status = 'active',
        block_reason = NULL,
        blocked_at = NULL,
        blocked_until = NULL,
        blocked_by = NULL,
        auto_block = FALSE,
        updated_at = NOW()
    WHERE blocked_until IS NOT NULL 
      AND blocked_until <= NOW();
    
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION cleanup_expired_blocks() TO authenticated;
GRANT EXECUTE ON FUNCTION update_account_block_status() TO authenticated;
