-- VitaChain Database Migration
-- Migration 08: Profile Schema Fixes
-- This migration fixes profile schema inconsistencies

-- Add role_data column to user_profiles table
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS role_data JSONB DEFAULT '{}';

-- Update user_profiles table to match backend expectations
-- Add indexes for role_data queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_role_data ON user_profiles USING GIN (role_data);

-- Add comments for documentation
COMMENT ON COLUMN user_profiles.role_data IS 'Role-specific data stored as JSONB';

-- Ensure all existing profiles have role_data
UPDATE user_profiles 
SET role_data = '{}' 
WHERE role_data IS NULL;

-- Add function to automatically combine first_name and last_name
CREATE OR REPLACE FUNCTION get_full_name(first_name TEXT, last_name TEXT) 
RETURNS TEXT AS $$
BEGIN
    RETURN COALESCE(TRIM(first_name || ' ' || last_name), '');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Add a generated column for full_name (optional, for convenience)
-- This is read-only and calculated from first_name and last_name
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS full_name TEXT GENERATED ALWAYS AS (get_full_name(first_name, last_name)) STORED;

-- Create index on the generated full_name column
CREATE INDEX IF NOT EXISTS idx_user_profiles_full_name ON user_profiles(full_name);
