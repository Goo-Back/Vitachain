-- AI Agronomic Recommendations Schema
-- Migration for Story 3-5: AI Agronomic Recommendations

-- Create ai_recommendations table for KATARA AI analysis
CREATE TABLE ai_recommendations (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    device_id           TEXT NOT NULL,
    farmer_id           UUID REFERENCES profiles(id) ON DELETE CASCADE,
    analysis_period_start TIMESTAMPTZ,
    analysis_period_end   TIMESTAMPTZ,
    telemetry_summary   JSONB,  -- Aggregated telemetry data
    ai_response         TEXT,   -- Full Claude API response
    recommendations     JSONB,  -- Structured recommendations
    confidence_score    FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    analysis_type       TEXT DEFAULT 'comprehensive' CHECK (analysis_type IN ('comprehensive','irrigation','health','soil')),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for recommendation queries
CREATE INDEX idx_recommendations_device_time ON ai_recommendations (device_id, created_at DESC);
CREATE INDEX idx_recommendations_farmer ON ai_recommendations (farmer_id, created_at DESC);
CREATE INDEX idx_recommendations_analysis_type ON ai_recommendations (analysis_type, created_at DESC);

-- Enable Row Level Security for AI recommendations
ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for ai_recommendations table
CREATE POLICY "farmers_own_their_recommendations" ON ai_recommendations
    FOR ALL USING (farmer_id = auth.uid());

CREATE POLICY "admins_can_view_all_recommendations" ON ai_recommendations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role = 'ADMIN'
        )
    );

-- Add recommendations_count column to profiles for easy tracking
ALTER TABLE profiles ADD COLUMN recommendations_count INTEGER DEFAULT 0;

-- Create trigger to update recommendations_count
CREATE OR REPLACE FUNCTION update_recommendations_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE profiles SET recommendations_count = recommendations_count + 1 WHERE id = NEW.farmer_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE profiles SET recommendations_count = recommendations_count - 1 WHERE id = OLD.farmer_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Handle farmer_id change if needed
        IF OLD.farmer_id != NEW.farmer_id THEN
            UPDATE profiles SET recommendations_count = recommendations_count - 1 WHERE id = OLD.farmer_id;
            UPDATE profiles SET recommendations_count = recommendations_count + 1 WHERE id = NEW.farmer_id;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for recommendations_count
CREATE TRIGGER update_recommendations_count_insert
    AFTER INSERT ON ai_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_recommendations_count();

CREATE TRIGGER update_recommendations_count_delete
    AFTER DELETE ON ai_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_recommendations_count();

CREATE TRIGGER update_recommendations_count_update
    AFTER UPDATE ON ai_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_recommendations_count();

-- Add comments for documentation
COMMENT ON TABLE ai_recommendations IS 'AI-generated agronomic recommendations for KATARA farmers';
COMMENT ON COLUMN ai_recommendations.device_id IS 'Foreign key to iot_devices.device_id';
COMMENT ON COLUMN ai_recommendations.farmer_id IS 'Reference to the farmer who requested this analysis';
COMMENT ON COLUMN ai_recommendations.analysis_period_start IS 'Start date for telemetry analysis period';
COMMENT ON COLUMN ai_recommendations.analysis_period_end IS 'End date for telemetry analysis period';
COMMENT ON COLUMN ai_recommendations.telemetry_summary IS 'Aggregated telemetry data used for analysis';
COMMENT ON COLUMN ai_recommendations.ai_response IS 'Full response from Claude AI API';
COMMENT ON COLUMN ai_recommendations.recommendations IS 'Structured recommendations in JSON format';
COMMENT ON COLUMN ai_recommendations.confidence_score IS 'AI confidence score (0-1)';
COMMENT ON COLUMN ai_recommendations.analysis_type IS 'Type of analysis performed';

-- Create a function to automatically create alerts for high-priority recommendations
CREATE OR REPLACE FUNCTION create_critical_recommendation_alert()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if any recommendation has high priority
    IF EXISTS (
        SELECT 1 FROM jsonb_each_text(NEW.recommendations) 
        WHERE value::jsonb->>'priority' = 'high'
    ) THEN
        -- Create a critical alert
        INSERT INTO katara_alerts (farmer_id, device_id, type, severity, message)
        VALUES (
            NEW.farmer_id,
            NEW.device_id,
            'ai_recommendation',
            'high',
            'High-priority AI recommendation generated. Check your recommendations for critical actions.'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic alert generation
CREATE TRIGGER create_alert_for_high_priority_recommendations
    AFTER INSERT ON ai_recommendations
    FOR EACH ROW EXECUTE FUNCTION create_critical_recommendation_alert();
