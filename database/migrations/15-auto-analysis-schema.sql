-- Migration 15: Automatic AI Analysis Schema Extensions
-- Adds support for automatic AI recommendation generation with trigger tracking
-- Story: 3-10-automatic-ai-recommendation-generation

-- Add automatic analysis columns to ai_recommendations table
ALTER TABLE ai_recommendations 
ADD COLUMN trigger_type TEXT CHECK (trigger_type IN ('manual','automatic_critical','automatic_periodic')),
ADD COLUMN trigger_conditions JSONB,  -- What triggered this analysis
ADD COLUMN analysis_priority TEXT CHECK (analysis_priority IN ('low','medium','high','critical')),
ADD COLUMN auto_analysis_enabled BOOLEAN DEFAULT TRUE;

-- Add automatic analysis settings to iot_devices table
ALTER TABLE iot_devices 
ADD COLUMN auto_analysis_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN last_auto_analysis TIMESTAMPTZ,
ADD COLUMN analysis_frequency_hours INT DEFAULT 6;

-- Create indexes for efficient automatic analysis queries
CREATE INDEX idx_recommendations_device_trigger_time 
  ON ai_recommendations (device_id, trigger_type, created_at DESC);

CREATE INDEX idx_devices_auto_analysis 
  ON iot_devices (auto_analysis_enabled, last_auto_analysis);

CREATE INDEX idx_recommendations_priority 
  ON ai_recommendations (analysis_priority, created_at DESC) 
  WHERE analysis_priority IN ('high', 'critical');

-- Add RLS policies for new columns (existing policies should cover these)
-- No new policies needed as they extend existing tables with same farmer_id ownership

-- Add comment documentation
COMMENT ON COLUMN ai_recommendations.trigger_type IS 'Type of trigger that initiated this AI analysis: manual, automatic_critical, or automatic_periodic';
COMMENT ON COLUMN ai_recommendations.trigger_conditions IS 'JSON object containing the conditions that triggered this automatic analysis';
COMMENT ON COLUMN ai_recommendations.analysis_priority IS 'Priority level of this analysis based on trigger conditions and recommendations';
COMMENT ON COLUMN ai_recommendations.auto_analysis_enabled IS 'Whether automatic analysis is enabled for this recommendation (legacy field)';

COMMENT ON COLUMN iot_devices.auto_analysis_enabled IS 'Whether automatic AI analysis is enabled for this device';
COMMENT ON COLUMN iot_devices.last_auto_analysis IS 'Timestamp of the last automatic analysis performed for this device';
COMMENT ON COLUMN iot_devices.analysis_frequency_hours IS 'Minimum hours between automatic analyses for this device';

-- Create a function to check if automatic analysis should be allowed
CREATE OR REPLACE FUNCTION should_allow_auto_analysis(
    device_id_param TEXT,
    farmer_id_param UUID
) RETURNS BOOLEAN AS $$
DECLARE
    last_analysis TIMESTAMPTZ;
    frequency_hours INT;
    auto_enabled BOOLEAN;
    device_exists BOOLEAN;
BEGIN
    -- Verify device ownership first (security check)
    SELECT EXISTS (
        SELECT 1 FROM iot_devices 
        WHERE device_id = device_id_param AND farmer_id = farmer_id_param
    ) INTO device_exists;
    
    -- If device not found or ownership invalid, return false
    IF NOT device_exists THEN
        RETURN FALSE;
    END IF;
    
    -- Get device settings
    SELECT auto_analysis_enabled, last_auto_analysis, analysis_frequency_hours
    INTO auto_enabled, last_analysis, frequency_hours
    FROM iot_devices 
    WHERE device_id = device_id_param AND farmer_id = farmer_id_param;
    
    -- If auto-analysis disabled, return false
    IF NOT auto_enabled THEN
        RETURN FALSE;
    END IF;
    
    -- If no previous analysis, allow it
    IF last_analysis IS NULL THEN
        RETURN TRUE;
    END IF;
    
    -- Check if enough time has passed
    RETURN (NOW() - last_analysis) >= (frequency_hours || ' hours')::INTERVAL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to update device last analysis timestamp
CREATE OR REPLACE FUNCTION update_device_last_analysis(
    device_id_param TEXT,
    farmer_id_param UUID
) RETURNS VOID AS $$
DECLARE
    device_exists BOOLEAN;
BEGIN
    -- Verify device ownership before update (security check)
    SELECT EXISTS (
        SELECT 1 FROM iot_devices 
        WHERE device_id = device_id_param AND farmer_id = farmer_id_param
    ) INTO device_exists;
    
    -- Only update if device exists and ownership is valid
    IF device_exists THEN
        UPDATE iot_devices 
        SET last_auto_analysis = NOW()
        WHERE device_id = device_id_param AND farmer_id = farmer_id_param;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to get devices due for periodic analysis
CREATE OR REPLACE FUNCTION get_devices_due_for_periodic_analysis() 
RETURNS TABLE(
    device_id TEXT,
    farmer_id UUID,
    auto_analysis_enabled BOOLEAN,
    last_auto_analysis TIMESTAMPTZ,
    analysis_frequency_hours INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.device_id,
        d.farmer_id,
        d.auto_analysis_enabled,
        d.last_auto_analysis,
        d.analysis_frequency_hours
    FROM iot_devices d
    WHERE d.auto_analysis_enabled = TRUE
      AND (
          d.last_auto_analysis IS NULL 
          OR (NOW() - d.last_auto_analysis) >= (d.analysis_frequency_hours || ' hours')::INTERVAL
      )
      AND EXISTS (
          SELECT 1 FROM telemetry_readings tr 
          WHERE tr.device_id = d.device_id 
            AND tr.timestamp >= NOW() - INTERVAL '7 days'
      )
    ORDER BY d.last_auto_analysis ASC NULLS FIRST;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
