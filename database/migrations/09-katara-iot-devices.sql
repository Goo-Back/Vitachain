-- KATARA IoT Device Registration Schema
-- Migration for Story 3-1: ESP32 Device Registration

-- Create iot_devices table for KATARA module
CREATE TABLE iot_devices (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    device_id     TEXT UNIQUE NOT NULL,      -- 'katara-{uuid4}'
    farmer_id     UUID REFERENCES profiles(id) ON DELETE CASCADE,
    name          TEXT,                       -- 'Parcelle Nord'
    location_lat  FLOAT CHECK (location_lat BETWEEN -90 AND 90),
    location_lng  FLOAT CHECK (location_lng BETWEEN -180 AND 180),
    registered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_iot_devices_device_id ON iot_devices (device_id);
CREATE INDEX idx_iot_devices_farmer_id ON iot_devices (farmer_id);
CREATE INDEX idx_iot_devices_registered_at ON iot_devices (registered_at DESC);

-- Enable Row Level Security
ALTER TABLE iot_devices ENABLE ROW LEVEL SECURITY;

-- RLS Policies for iot_devices table
CREATE POLICY "farmers_own_their_devices" ON iot_devices
    FOR ALL USING (farmer_id = auth.uid());

CREATE POLICY "admins_can_view_all_devices" ON iot_devices
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role = 'ADMIN'
        )
    );

-- Create telemetry_readings table for future story 3-2
CREATE TABLE telemetry_readings (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    device_id     TEXT NOT NULL,
    farmer_id     UUID REFERENCES profiles(id) ON DELETE CASCADE,
    temperature   FLOAT CHECK (temperature BETWEEN -10 AND 60),
    humidity      FLOAT CHECK (humidity BETWEEN 0 AND 100),
    ndvi          FLOAT CHECK (ndvi BETWEEN -1 AND 1),
    battery_level FLOAT CHECK (battery_level BETWEEN 0 AND 100),
    timestamp     TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for telemetry queries
CREATE INDEX idx_telemetry_device_time ON telemetry_readings (device_id, timestamp DESC);
CREATE INDEX idx_telemetry_farmer ON telemetry_readings (farmer_id, timestamp DESC);

-- Enable Row Level Security for telemetry
ALTER TABLE telemetry_readings ENABLE ROW LEVEL SECURITY;

-- RLS Policies for telemetry_readings table
CREATE POLICY "farmers_read_own_telemetry" ON telemetry_readings
    FOR SELECT USING (farmer_id = auth.uid());

CREATE POLICY "service_role_insert_telemetry" ON telemetry_readings
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "admins_can_view_all_telemetry" ON telemetry_readings
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role = 'ADMIN'
        )
    );

-- Create katara_alerts table for future stories
CREATE TABLE katara_alerts (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    farmer_id   UUID REFERENCES profiles(id) NOT NULL,
    device_id   TEXT,
    type        TEXT NOT NULL,  -- 'threshold_exceeded' | 'ai_recommendation' | 'weather_risk'
    severity    TEXT CHECK (severity IN ('low','medium','high','critical')),
    message     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for alerts queries
CREATE INDEX idx_alerts_farmer_unread ON katara_alerts (farmer_id, is_read, created_at DESC);
CREATE INDEX idx_alerts_device ON katara_alerts (device_id, created_at DESC);

-- Enable Row Level Security for alerts
ALTER TABLE katara_alerts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for katara_alerts table
CREATE POLICY "farmers_read_own_alerts" ON katara_alerts
    FOR SELECT USING (farmer_id = auth.uid());

CREATE POLICY "farmers_mark_read" ON katara_alerts
    FOR UPDATE USING (farmer_id = auth.uid());

CREATE POLICY "service_role_manage_alerts" ON katara_alerts
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "admins_can_view_all_alerts" ON katara_alerts
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role = 'ADMIN'
        )
    );

-- Add device_count column to profiles for easy tracking
ALTER TABLE profiles ADD COLUMN devices_count INTEGER DEFAULT 0;

-- Create trigger to update devices_count
CREATE OR REPLACE FUNCTION update_devices_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE profiles SET devices_count = devices_count + 1 WHERE id = NEW.farmer_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE profiles SET devices_count = devices_count - 1 WHERE id = OLD.farmer_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Handle farmer_id change if needed
        IF OLD.farmer_id != NEW.farmer_id THEN
            UPDATE profiles SET devices_count = devices_count - 1 WHERE id = OLD.farmer_id;
            UPDATE profiles SET devices_count = devices_count + 1 WHERE id = NEW.farmer_id;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for devices_count
CREATE TRIGGER update_devices_count_insert
    AFTER INSERT ON iot_devices
    FOR EACH ROW EXECUTE FUNCTION update_devices_count();

CREATE TRIGGER update_devices_count_delete
    AFTER DELETE ON iot_devices
    FOR EACH ROW EXECUTE FUNCTION update_devices_count();

CREATE TRIGGER update_devices_count_update
    AFTER UPDATE ON iot_devices
    FOR EACH ROW EXECUTE FUNCTION update_devices_count();

-- Add comments for documentation
COMMENT ON TABLE iot_devices IS 'KATARA IoT device registration table for ESP32 sensors';
COMMENT ON TABLE telemetry_readings IS 'Time-series telemetry data from IoT devices';
COMMENT ON TABLE katara_alerts IS 'Alerts and recommendations for farmers';

COMMENT ON COLUMN iot_devices.device_id IS 'Unique device identifier in format katara-{uuid4}';
COMMENT ON COLUMN iot_devices.farmer_id IS 'Reference to the farmer who owns this device';
COMMENT ON COLUMN iot_devices.name IS 'Human-readable device name (e.g., Parcelle Nord)';
COMMENT ON COLUMN iot_devices.location_lat IS 'Device latitude coordinate';
COMMENT ON COLUMN iot_devices.location_lng IS 'Device longitude coordinate';

COMMENT ON COLUMN telemetry_readings.device_id IS 'Foreign key to iot_devices.device_id';
COMMENT ON COLUMN telemetry_readings.temperature IS 'Temperature reading in Celsius';
COMMENT ON COLUMN telemetry_readings.humidity IS 'Humidity percentage';
COMMENT ON COLUMN telemetry_readings.ndvi IS 'Normalized Difference Vegetation Index';
COMMENT ON COLUMN telemetry_readings.battery_level IS 'Device battery percentage';
