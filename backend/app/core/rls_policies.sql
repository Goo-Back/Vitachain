-- VitaChain RLS Policies for Row-Level Security
-- Integrates with RBAC system for comprehensive access control

-- Enable RLS on all user tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Functions for permission checking
CREATE OR REPLACE FUNCTION rls.uses_role(
    user_role text,
    table_name text,
    operation text
) RETURNS boolean AS $$
BEGIN
    -- Check if user has required role for table/operation
    -- Admin has access to everything
    IF user_role = 'ADMIN' THEN
        RETURN true;
    
    -- Support has read access to most tables
    IF user_role = 'SUPPORT' THEN
        RETURN table_name IN ('profiles', 'users', 'audit_logs');
    
    -- Farmer permissions
    IF user_role = 'FARMER' THEN
        CASE 
            WHEN table_name = 'telemetry' AND operation = 'SELECT' THEN RETURN true;
            WHEN table_name = 'devices' AND operation IN ('SELECT', 'INSERT', 'UPDATE') THEN RETURN true;
            WHEN table_name = 'alerts' AND operation IN ('SELECT', 'INSERT', 'UPDATE') THEN RETURN true;
            WHEN table_name = 'listings' AND operation IN ('SELECT', 'INSERT', 'UPDATE') THEN RETURN true;
            WHEN table_name = 'profiles' AND operation = 'UPDATE' THEN RETURN true;
            ELSE RETURN false;
        END;
    
    -- Restaurant permissions
    IF user_role = 'RESTAURANT' THEN
        CASE 
            WHEN table_name = 'meals' AND operation IN ('SELECT', 'INSERT', 'UPDATE') THEN RETURN true;
            WHEN table_name = 'reservations' AND operation IN ('SELECT', 'INSERT', 'UPDATE') THEN RETURN true;
            WHEN table_name = 'profiles' AND operation = 'UPDATE' THEN RETURN true;
            ELSE RETURN false;
        END;
    
    -- Citizen permissions
    IF user_role = 'CITIZEN' THEN
        CASE 
            WHEN table_name = 'reservations' AND operation IN ('SELECT', 'INSERT') THEN RETURN true;
            WHEN table_name = 'profiles' AND operation = 'UPDATE' THEN RETURN true;
            ELSE RETURN false;
        END;
    
    -- Default deny for other roles/tables
    RETURN false;
END;
$$ LANGUAGE plpgsql;

-- RLS Functions for ownership checking
CREATE OR REPLACE FUNCTION rls.check_ownership(
    user_id text,
    resource_user_id text,
    table_name text
) RETURNS boolean AS $$
BEGIN
    -- Admin and Support can access all resources
    -- Check if user is admin or support from current session
    -- This would need to be passed from auth context
    IF EXISTS (
        SELECT 1 FROM auth_sessions 
        WHERE user_id = user_id 
        AND role IN ('ADMIN', 'SUPPORT')
    ) THEN
        RETURN true;
    
    -- Users can only access their own resources
    RETURN user_id = resource_user_id;
END;
$$ LANGUAGE plpgsql;

-- RLS Functions for policy checking
CREATE OR REPLACE FUNCTION rls.check_permission(
    user_role text,
    user_id text,
    table_name text,
    condition text DEFAULT 'true'
) RETURNS boolean AS $$
BEGIN
    -- First check if user has role-based access
    IF NOT rls.uses_role(user_role, table_name, 'SELECT') THEN
        RETURN false;
    
    -- Then check ownership for user-specific resources
    IF table_name IN ('telemetry', 'devices', 'alerts', 'listings', 'meals', 'reservations') THEN
        RETURN rls.check_ownership(user_id, resource_user_id, table_name);
    
    -- For other tables, just check role
    RETURN rls.uses_role(user_role, table_name, 'SELECT');
END;
$$ LANGUAGE plpgsql;

-- RLS Policies for each table

-- Profiles table RLS
CREATE POLICY profiles_select_policy ON profiles
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'profiles', 'SELECT') 
           AND rls.check_permission(auth.jwt() ->> 'role', auth.jwt() ->> 'user_id', 'profiles', 'true'));

CREATE POLICY profiles_update_policy ON profiles
    FOR UPDATE
    USING (rls.uses_role(auth.jwt() ->> 'role', 'profiles', 'UPDATE') 
           AND rls.check_permission(auth.jwt() ->> 'role', auth.jwt() ->> 'user_id', 'profiles', 'true')
           AND rls.check_ownership(auth.jwt() ->> 'user_id', auth.jwt() ->> 'id', 'profiles'));

-- Telemetry table RLS
CREATE POLICY telemetry_select_policy ON telemetry
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'telemetry', 'SELECT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', telemetry.farmer_id, 'telemetry'));

CREATE POLICY telemetry_insert_policy ON telemetry
    FOR INSERT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'telemetry', 'INSERT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', telemetry.farmer_id, 'telemetry'));

-- Devices table RLS
CREATE POLICY devices_select_policy ON devices
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'devices', 'SELECT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', devices.farmer_id, 'devices'));

CREATE POLICY devices_update_policy ON devices
    FOR UPDATE
    USING (rls.uses_role(auth.jwt() ->> 'role', 'devices', 'UPDATE') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', devices.farmer_id, 'devices'));

-- Alerts table RLS
CREATE POLICY alerts_select_policy ON alerts
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'alerts', 'SELECT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', alerts.farmer_id, 'alerts'));

CREATE POLICY alerts_insert_policy ON alerts
    FOR INSERT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'alerts', 'INSERT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', alerts.farmer_id, 'alerts'));

CREATE POLICY alerts_update_policy ON alerts
    FOR UPDATE
    USING (rls.uses_role(auth.jwt() ->> 'role', 'alerts', 'UPDATE') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', alerts.farmer_id, 'alerts'));

-- Listings table RLS
CREATE POLICY listings_select_policy ON listings
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'listings', 'SELECT'));

CREATE POLICY listings_insert_policy ON listings
    FOR INSERT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'listings', 'INSERT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', listings.farmer_id, 'listings'));

CREATE POLICY listings_update_policy ON listings
    FOR UPDATE
    USING (rls.uses_role(auth.jwt() ->> 'role', 'listings', 'UPDATE') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', listings.farmer_id, 'listings'));

-- Orders table RLS
CREATE POLICY orders_select_policy ON orders
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'orders', 'SELECT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', orders.customer_id, 'orders'));

CREATE POLICY orders_insert_policy ON orders
    FOR INSERT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'orders', 'INSERT') 
           AND rls.check_permission(auth.jwt() ->> 'role', auth.jwt() ->> 'user_id', 'orders', 'true'));

-- Meals table RLS
CREATE POLICY meals_select_policy ON meals
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'meals', 'SELECT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', meals.restaurant_id, 'meals'));

CREATE POLICY meals_insert_policy ON meals
    FOR INSERT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'meals', 'INSERT') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', meals.restaurant_id, 'meals'));

CREATE POLICY meals_update_policy ON meals
    FOR UPDATE
    USING (rls.uses_role(auth.jwt() ->> 'role', 'meals', 'UPDATE') 
           AND rls.check_ownership(auth.jwt() ->> 'user_id', meals.restaurant_id, 'meals'));

-- Reservations table RLS
CREATE POLICY reservations_select_policy ON reservations
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'reservations', 'SELECT'));

CREATE POLICY reservations_insert_policy ON reservations
    FOR INSERT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'reservations', 'INSERT') 
           AND rls.check_permission(auth.jwt() ->> 'role', auth.jwt() ->> 'user_id', 'reservations', 'true'));

-- Users table RLS (Admin/Support only)
CREATE POLICY users_select_policy ON users
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'users', 'SELECT'));

-- Audit logs table RLS (Admin/Support only)
CREATE POLICY audit_logs_select_policy ON audit_logs
    FOR SELECT
    USING (rls.uses_role(auth.jwt() ->> 'role', 'audit_logs', 'SELECT'));

-- Apply all policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE reservations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
