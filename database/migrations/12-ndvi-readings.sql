-- Migration 12: NDVI Readings Table and RLS Policies
-- Story: 3-7-satellite-ndvi-imagery
-- Purpose: Store NDVI satellite imagery data from Sentinel Hub API with RLS protection

-- Create ndvi_readings table
CREATE TABLE IF NOT EXISTS ndvi_readings (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id       TEXT NOT NULL,
  farmer_id       UUID REFERENCES profiles(id) ON DELETE CASCADE,
  location_lat    FLOAT NOT NULL,
  location_lng    FLOAT NOT NULL,
  ndvi_value      FLOAT CHECK (ndvi_value BETWEEN -1 AND 1),
  ndvi_trend      TEXT CHECK (ndvi_trend IN ('improving','stable','declining','critical')),
  imagery_url     TEXT,                    -- Sentinel Hub imagery URL
  cloud_cover    FLOAT CHECK (cloud_cover BETWEEN 0 AND 100),
  data_quality   TEXT CHECK (data_quality IN ('excellent','good','fair','poor')),
  acquisition_date TIMESTAMPTZ,         -- Satellite image capture time
  api_source      TEXT DEFAULT 'sentinel_hub',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ndvi_device_time 
ON ndvi_readings (device_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ndvi_farmer 
ON ndvi_readings (farmer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ndvi_location 
ON ndvi_readings USING GIST (point(location_lng, location_lat));

CREATE INDEX IF NOT EXISTS idx_ndvi_created_at 
ON ndvi_readings (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ndvi_acquisition_date 
ON ndvi_readings (acquisition_date DESC);

-- Enable Row Level Security
ALTER TABLE ndvi_readings ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for migration safety)
DROP POLICY IF EXISTS "farmers_own_their_ndvi_data" ON ndvi_readings;

-- Create RLS policies
-- Farmers can only read their own NDVI data
CREATE POLICY "farmers_own_their_ndvi_data" ON ndvi_readings
FOR SELECT USING (farmer_id = auth.uid());

-- Farmers can only insert their own NDVI data
CREATE POLICY "farmers_insert_their_ndvi_data" ON ndvi_readings
FOR INSERT WITH CHECK (farmer_id = auth.uid());

-- Admins can read all NDVI data
CREATE POLICY "admins_read_all_ndvi_data" ON ndvi_readings
FOR SELECT USING (auth.jwt()->>'role' = 'ADMIN');

-- No update or delete policies - NDVI data is immutable once created

-- Add comments for documentation
COMMENT ON TABLE ndvi_readings IS 'Stores NDVI satellite imagery data from Sentinel Hub API for KATARA devices';
COMMENT ON COLUMN ndvi_readings.device_id IS 'KATARA device identifier (format: katara-{uuid})';
COMMENT ON COLUMN ndvi_readings.farmer_id IS 'Foreign key to profiles table - owner of the NDVI data';
COMMENT ON COLUMN ndvi_readings.location_lat IS 'Latitude of NDVI reading location';
COMMENT ON COLUMN ndvi_readings.location_lng IS 'Longitude of NDVI reading location';
COMMENT ON COLUMN ndvi_readings.ndvi_value IS 'NDVI value (-1 to 1, vegetation typically 0.2-0.8)';
COMMENT ON COLUMN ndvi_readings.ndvi_trend IS 'NDVI trend direction (improving, stable, declining, critical)';
COMMENT ON COLUMN ndvi_readings.imagery_url IS 'URL to Sentinel Hub NDVI imagery';
COMMENT ON COLUMN ndvi_readings.cloud_cover IS 'Cloud cover percentage (0-100)';
COMMENT ON COLUMN ndvi_readings.data_quality IS 'Data quality assessment (excellent, good, fair, poor)';
COMMENT ON COLUMN ndvi_readings.acquisition_date IS 'Timestamp when satellite image was captured';
COMMENT ON COLUMN ndvi_readings.api_source IS 'Source of NDVI data (currently Sentinel Hub)';
COMMENT ON COLUMN ndvi_readings.created_at IS 'Timestamp when NDVI data was retrieved';

-- Function to clean up old NDVI data (90-day retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_ndvi_data()
RETURNS void AS $$
BEGIN
    DELETE FROM ndvi_readings 
    WHERE created_at < NOW() - INTERVAL '90 days';
    
    RAISE NOTICE 'Cleaned up old NDVI data older than 90 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION cleanup_old_ndvi_data() TO authenticated;

-- Add validation constraints
ALTER TABLE ndvi_readings 
ADD CONSTRAINT IF NOT EXISTS check_ndvi_value 
CHECK (ndvi_value IS NULL OR (ndvi_value >= -1 AND ndvi_value <= 1));

ALTER TABLE ndvi_readings 
ADD CONSTRAINT IF NOT EXISTS check_cloud_cover 
CHECK (cloud_cover IS NULL OR (cloud_cover >= 0 AND cloud_cover <= 100));

ALTER TABLE ndvi_readings 
ADD CONSTRAINT IF NOT EXISTS check_location_lat 
CHECK (location_lat >= -90 AND location_lat <= 90);

ALTER TABLE ndvi_readings 
ADD CONSTRAINT IF NOT EXISTS check_location_lng 
CHECK (location_lng >= -180 AND location_lng <= 180);

-- Add device_id foreign key constraint (references iot_devices table)
ALTER TABLE ndvi_readings 
ADD CONSTRAINT IF NOT EXISTS fk_ndvi_device 
FOREIGN KEY (device_id) REFERENCES iot_devices(device_id) ON DELETE CASCADE;

-- Create trigger function for NDVI trend analysis
CREATE OR REPLACE FUNCTION analyze_ndvi_trend()
RETURNS TRIGGER AS $$
BEGIN
    -- This function could be called periodically to update NDVI trends
    -- For now, it's a placeholder for future trend analysis
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;
