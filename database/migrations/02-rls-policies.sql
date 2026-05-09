-- VitaChain Row Level Security Policies
-- Migration 02: RLS Policy Configuration
-- This migration enables RLS and creates security policies for all tables

-- Enable Row Level Security on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensors ENABLE ROW LEVEL SECURITY;
ALTER TABLE telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE pickup_slots ENABLE ROW LEVEL SECURITY;
ALTER TABLE reservations ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE in_app_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Service role can manage all users" ON users
    FOR ALL USING (auth.role() = 'service_role');

-- User Profiles table policies
CREATE POLICY "Users can view own profile details" ON user_profiles
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own profile details" ON user_profiles
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Admins can view all profiles" ON user_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage all profiles" ON user_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Roles table policies (read-only for most users)
CREATE POLICY "Authenticated users can view roles" ON roles
    FOR SELECT USING (auth.role() != 'anon');

CREATE POLICY "Service role can manage roles" ON roles
    FOR ALL USING (auth.role() = 'service_role');

-- Devices table policies
CREATE POLICY "Users can view own devices" ON devices
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can manage own devices" ON devices
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY "Admins can view all devices" ON devices
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage all devices" ON devices
    FOR ALL USING (auth.role() = 'service_role');

-- Sensors table policies
CREATE POLICY "Users can view own device sensors" ON sensors
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM devices 
            WHERE id = device_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage own device sensors" ON sensors
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM devices 
            WHERE id = device_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can manage all sensors" ON sensors
    FOR ALL USING (auth.role() = 'service_role');

-- Telemetry table policies
CREATE POLICY "Users can view own device telemetry" ON telemetry
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM devices 
            WHERE id = device_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own device telemetry" ON telemetry
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM devices 
            WHERE id = device_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can manage all telemetry" ON telemetry
    FOR ALL USING (auth.role() = 'service_role');

-- Products table policies
CREATE POLICY "Users can view active products" ON products
    FOR SELECT USING (is_active = true);

CREATE POLICY "Farmers can manage own products" ON products
    FOR ALL USING (auth.uid()::text = farmer_id::text);

CREATE POLICY "Admins can view all products" ON products
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage all products" ON products
    FOR ALL USING (auth.role() = 'service_role');

-- Orders table policies
CREATE POLICY "Users can view own orders" ON orders
    FOR SELECT USING (auth.uid()::text = buyer_id::text);

CREATE POLICY "Users can create own orders" ON orders
    FOR INSERT WITH CHECK (auth.uid()::text = buyer_id::text);

CREATE POLICY "Users can update own orders" ON orders
    FOR UPDATE USING (auth.uid()::text = buyer_id::text);

CREATE POLICY "Farmers can view orders for their products" ON orders
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = orders.id
            AND p.farmer_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all orders" ON orders
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage all orders" ON orders
    FOR ALL USING (auth.role() = 'service_role');

-- Order Items table policies
CREATE POLICY "Users can view own order items" ON order_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM orders 
            WHERE id = order_id 
            AND buyer_id = auth.uid()
        )
    );

CREATE POLICY "Farmers can view order items for their products" ON order_items
    FOR SELECT USING (auth.uid()::text = farmer_id::text);

CREATE POLICY "Service role can manage all order items" ON order_items
    FOR ALL USING (auth.role() = 'service_role');

-- Meals table policies
CREATE POLICY "Users can view active meals" ON meals
    FOR SELECT USING (is_active = true);

CREATE POLICY "Restaurants can manage own meals" ON meals
    FOR ALL USING (auth.uid()::text = restaurant_id::text);

CREATE POLICY "Admins can view all meals" ON meals
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage all meals" ON meals
    FOR ALL USING (auth.role() = 'service_role');

-- Pickup Slots table policies
CREATE POLICY "Users can view active pickup slots" ON pickup_slots
    FOR SELECT USING (is_active = true);

CREATE POLICY "Restaurants can manage own meal pickup slots" ON pickup_slots
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM meals 
            WHERE id = meal_id 
            AND restaurant_id = auth.uid()
        )
    );

CREATE POLICY "Service role can manage all pickup slots" ON pickup_slots
    FOR ALL USING (auth.role() = 'service_role');

-- Reservations table policies
CREATE POLICY "Users can view own reservations" ON reservations
    FOR SELECT USING (auth.uid()::text = citizen_id::text);

CREATE POLICY "Users can create own reservations" ON reservations
    FOR INSERT WITH CHECK (auth.uid()::text = citizen_id::text);

CREATE POLICY "Users can update own reservations" ON reservations
    FOR UPDATE USING (auth.uid()::text = citizen_id::text);

CREATE POLICY "Restaurants can view reservations for their meals" ON reservations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM meals 
            WHERE id = meal_id 
            AND restaurant_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all reservations" ON reservations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage all reservations" ON reservations
    FOR ALL USING (auth.role() = 'service_role');

-- Alerts table policies
CREATE POLICY "Users can view own alerts" ON alerts
    FOR SELECT USING (auth.uid()::text = user_id::text OR user_id IS NULL);

CREATE POLICY "Users can update own alerts" ON alerts
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "System can create alerts" ON alerts
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR user_id IS NULL);

CREATE POLICY "Service role can manage all alerts" ON alerts
    FOR ALL USING (auth.role() = 'service_role');

-- Email Notifications table policies
CREATE POLICY "Users can view own email notifications" ON email_notifications
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Service role can manage all email notifications" ON email_notifications
    FOR ALL USING (auth.role() = 'service_role');

-- In-App Notifications table policies
CREATE POLICY "Users can view own notifications" ON in_app_notifications
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own notifications" ON in_app_notifications
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "System can create notifications" ON in_app_notifications
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all notifications" ON in_app_notifications
    FOR ALL USING (auth.role() = 'service_role');

-- Audit Logs table policies (read-only for admins)
CREATE POLICY "Admins can view audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage audit logs" ON audit_logs
    FOR ALL USING (auth.role() = 'service_role');

-- System Metrics table policies
CREATE POLICY "Admins can view system metrics" ON system_metrics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage system metrics" ON system_metrics
    FOR ALL USING (auth.role() = 'service_role');

-- Support Tickets table policies
CREATE POLICY "Users can view own support tickets" ON support_tickets
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create own support tickets" ON support_tickets
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own support tickets" ON support_tickets
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Support staff can view assigned tickets" ON support_tickets
    FOR SELECT USING (assigned_to = auth.uid());

CREATE POLICY "Support staff can manage assigned tickets" ON support_tickets
    FOR UPDATE USING (assigned_to = auth.uid());

CREATE POLICY "Admins can view all support tickets" ON support_tickets
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() 
            AND role = 'admin'
        )
    );

CREATE POLICY "Service role can manage all support tickets" ON support_tickets
    FOR ALL USING (auth.role() = 'service_role');

-- Create function to check user role
CREATE OR REPLACE FUNCTION check_user_role(user_uuid UUID, required_role user_role)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_profiles 
        WHERE user_id = user_uuid 
        AND role = required_role
        AND is_active = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check if user owns resource
CREATE OR REPLACE FUNCTION check_resource_owner(resource_user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN resource_user_id = auth.uid();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function for telemetry data access (for device API)
CREATE OR REPLACE FUNCTION can_access_device_telemetry(device_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM devices 
        WHERE id = device_uuid 
        AND user_id = auth.uid()
        AND status = 'active'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function for order access (farmers viewing orders for their products)
CREATE OR REPLACE FUNCTION can_view_order_details(order_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Buyer can always view their own orders
    IF EXISTS (SELECT 1 FROM orders WHERE id = order_uuid AND buyer_id = auth.uid()) THEN
        RETURN true;
    END IF;
    
    -- Farmers can view orders containing their products
    IF EXISTS (
        SELECT 1 FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = order_uuid
        AND p.farmer_id = auth.uid()
    ) THEN
        RETURN true;
    END IF;
    
    -- Admins can view all orders
    IF check_user_role(auth.uid(), 'admin') THEN
        RETURN true;
    END IF;
    
    RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function for reservation access
CREATE OR REPLACE FUNCTION can_view_reservation_details(reservation_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Citizens can view their own reservations
    IF EXISTS (SELECT 1 FROM reservations WHERE id = reservation_uuid AND citizen_id = auth.uid()) THEN
        RETURN true;
    END IF;
    
    -- Restaurants can view reservations for their meals
    IF EXISTS (
        SELECT 1 FROM reservations r
        JOIN meals m ON r.meal_id = m.id
        WHERE r.id = reservation_uuid
        AND m.restaurant_id = auth.uid()
    ) THEN
        RETURN true;
    END IF;
    
    -- Admins can view all reservations
    IF check_user_role(auth.uid(), 'admin') THEN
        RETURN true;
    END IF;
    
    RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON roles TO anon;

-- Grant execute permissions on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated, service_role;
