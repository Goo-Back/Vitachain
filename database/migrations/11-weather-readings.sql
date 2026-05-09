-- Migration 11: Weather Readings Table and RLS Policies
-- Story: 3-6-weather-data-integration
-- Purpose: Store weather data from OpenWeatherMap API with RLS protection

-- Create weather_readings table
CREATE TABLE IF NOT EXISTS weather_readings (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id       TEXT NOT NULL,
  farmer_id       UUID REFERENCES profiles(id) ON DELETE CASCADE,
  location_lat    FLOAT NOT NULL,
  location_lng    FLOAT NOT NULL,
  temperature     FLOAT,           -- Current temperature (°C)
  humidity        FLOAT,           -- Current humidity (%)
  pressure        FLOAT,           -- Atmospheric pressure (hPa)
  wind_speed      FLOAT,           -- Wind speed (m/s)
  wind_direction  FLOAT,           -- Wind direction (degrees)
  rainfall_1h     FLOAT,           -- Rainfall in last 1 hour (mm)
  rainfall_24h    FLOAT,           -- Rainfall in last 24 hours (mm)
  weather_main    TEXT,            -- Main weather condition (Rain, Clear, etc.)
  weather_description TEXT,        -- Detailed weather description
  visibility      FLOAT,           -- Visibility (km)
  uv_index        FLOAT,           -- UV index (if available)
  forecast_data   JSONB,           -- 24-hour forecast data
  api_source      TEXT DEFAULT 'openweathermap',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_weather_device_time 
ON weather_readings (device_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_weather_farmer 
ON weather_readings (farmer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_weather_location 
ON weather_readings USING GIST (point(location_lng, location_lat));

CREATE INDEX IF NOT EXISTS idx_weather_created_at 
ON weather_readings (created_at DESC);

-- Enable Row Level Security
ALTER TABLE weather_readings ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for migration safety)
DROP POLICY IF EXISTS "farmers_own_their_weather_data" ON weather_readings;

-- Create RLS policies
-- Farmers can only read their own weather data
CREATE POLICY "farmers_own_their_weather_data" ON weather_readings
FOR SELECT USING (farmer_id = auth.uid());

-- Farmers can only insert their own weather data
CREATE POLICY "farmers_insert_their_weather_data" ON weather_readings
FOR INSERT WITH CHECK (farmer_id = auth.uid());

-- Admins can read all weather data
CREATE POLICY "admins_read_all_weather_data" ON weather_readings
FOR SELECT USING (auth.jwt()->>'role' = 'ADMIN');

-- No update or delete policies - weather data is immutable once created

-- Add comments for documentation
COMMENT ON TABLE weather_readings IS 'Stores weather data from OpenWeatherMap API for KATARA devices';
COMMENT ON COLUMN weather_readings.device_id IS 'KATARA device identifier (format: katara-{uuid})';
COMMENT ON COLUMN weather_readings.farmer_id IS 'Foreign key to profiles table - owner of the weather data';
COMMENT ON COLUMN weather_readings.location_lat IS 'Latitude of weather reading location';
COMMENT ON COLUMN weather_readings.location_lng IS 'Longitude of weather reading location';
COMMENT ON COLUMN weather_readings.temperature IS 'Current temperature in Celsius';
COMMENT ON COLUMN weather_readings.humidity IS 'Current humidity percentage (0-100)';
COMMENT ON COLUMN weather_readings.pressure IS 'Atmospheric pressure in hPa';
COMMENT ON COLUMN weather_readings.wind_speed IS 'Wind speed in meters per second';
COMMENT ON COLUMN weather_readings.wind_direction IS 'Wind direction in degrees (0-360)';
COMMENT ON COLUMN weather_readings.rainfall_1h IS 'Rainfall in the last hour in millimeters';
COMMENT ON COLUMN weather_readings.rainfall_24h IS 'Rainfall in the last 24 hours in millimeters';
COMMENT ON COLUMN weather_readings.weather_main IS 'Main weather condition (e.g., Rain, Clear, Clouds)';
COMMENT ON COLUMN weather_readings.weather_description IS 'Detailed weather description in French';
COMMENT ON COLUMN weather_readings.visibility IS 'Visibility in kilometers';
COMMENT ON COLUMN weather_readings.uv_index IS 'UV index (if available from API)';
COMMENT ON COLUMN weather_readings.forecast_data IS '24-hour forecast data as JSONB';
COMMENT ON COLUMN weather_readings.api_source IS 'Source of weather data (currently OpenWeatherMap)';
COMMENT ON COLUMN weather_readings.created_at IS 'Timestamp when weather data was retrieved';

-- Function to clean up old weather data (30-day retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_weather_data()
RETURNS void AS $$
BEGIN
    DELETE FROM weather_readings 
    WHERE created_at < NOW() - INTERVAL '30 days';
    
    RAISE NOTICE 'Cleaned up old weather data older than 30 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION cleanup_old_weather_data() TO authenticated;

-- Create a scheduled job trigger (if using pg_cron extension)
-- This would be set up separately in the database configuration
-- SELECT cron.schedule('cleanup-weather-data', '0 2 * * *', 'SELECT cleanup_old_weather_data();');

-- Add validation constraints
ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_temperature 
CHECK (temperature IS NULL OR temperature BETWEEN -50 AND 60);

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_humidity 
CHECK (humidity IS NULL OR (humidity >= 0 AND humidity <= 100));

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_pressure 
CHECK (pressure IS NULL OR (pressure >= 800 AND pressure <= 1200));

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_wind_speed 
CHECK (wind_speed IS NULL OR (wind_speed >= 0 AND wind_speed <= 100));

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_wind_direction 
CHECK (wind_direction IS NULL OR (wind_direction >= 0 AND wind_direction <= 360));

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_rainfall_1h 
CHECK (rainfall_1h IS NULL OR (rainfall_1h >= 0 AND rainfall_1h <= 200));

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_rainfall_24h 
CHECK (rainfall_24h IS NULL OR (rainfall_24h >= 0 AND rainfall_24h <= 500));

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_visibility 
CHECK (visibility IS NULL OR (visibility >= 0 AND visibility <= 50));

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_uv_index 
CHECK (uv_index IS NULL OR (uv_index >= 0 AND uv_index <= 15));

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_location_lat 
CHECK (location_lat >= -90 AND location_lat <= 90);

ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS check_location_lng 
CHECK (location_lng >= -180 AND location_lng <= 180);

-- Add device_id foreign key constraint (references iot_devices table)
ALTER TABLE weather_readings 
ADD CONSTRAINT IF NOT EXISTS fk_weather_device 
FOREIGN KEY (device_id) REFERENCES iot_devices(device_id) ON DELETE CASCADE;

COMMIT;
