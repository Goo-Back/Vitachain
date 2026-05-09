-- Alert Read/Unread Management Schema Update
-- Migration for Story 3-9: Alert Read/Unread Management

-- Update katara_alerts table to match story requirements
-- Add read_status column (replacing is_read) and read_at timestamp
ALTER TABLE katara_alerts 
ADD COLUMN read_status BOOLEAN DEFAULT FALSE,
ADD COLUMN read_at TIMESTAMPTZ;

-- Migrate existing data from is_read to read_status
UPDATE katara_alerts 
SET read_status = COALESCE(is_read, FALSE),
    read_at = CASE 
        WHEN COALESCE(is_read, FALSE) = TRUE THEN created_at + INTERVAL '1 hour'  -- Assume read 1 hour after creation
        ELSE NULL 
    END;

-- Drop the old is_read column
ALTER TABLE katara_alerts DROP COLUMN is_read;

-- Create new indexes for performance
CREATE INDEX idx_katara_alerts_read_status 
ON katara_alerts(farmer_id, read_status, created_at DESC);

-- Update existing indexes that referenced is_read
DROP INDEX IF EXISTS idx_alerts_farmer_unread;
CREATE INDEX idx_alerts_farmer_unread 
ON katara_alerts(farmer_id, read_status, created_at DESC);

-- Update RLS Policies to use new column names
DROP POLICY IF EXISTS "farmers_mark_read" ON katara_alerts;

CREATE POLICY "farmers_update_own_alert_status" ON katara_alerts
    FOR UPDATE USING (farmer_id = auth.uid())
    WITH CHECK (farmer_id = auth.uid());

-- Add function to automatically set read_at when status changes
CREATE OR REPLACE FUNCTION set_read_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- Set read_at when marking as read
    IF NEW.read_status = TRUE AND (OLD.read_status IS FALSE OR OLD.read_status IS NULL) THEN
        NEW.read_at = NOW();
    -- Clear read_at when marking as unread
    ELSIF NEW.read_status = FALSE AND OLD.read_status = TRUE THEN
        NEW.read_at = NULL;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically manage read_at timestamp
CREATE TRIGGER alert_read_status_trigger
    BEFORE UPDATE ON katara_alerts
    FOR EACH ROW EXECUTE FUNCTION set_read_timestamp();

-- Add comments for documentation
COMMENT ON COLUMN katara_alerts.read_status IS 'Alert read/unread status (true=read, false=unread)';
COMMENT ON COLUMN katara_alerts.read_at IS 'Timestamp when alert was marked as read (null if unread)';
COMMENT ON FUNCTION set_read_timestamp() IS 'Automatically sets/clears read_at based on read_status changes';
