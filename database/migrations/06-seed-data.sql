-- VitaChain Seed Data
-- Migration 06: Initial Seed Data
-- This migration inserts initial data for testing and development

-- Disable audit triggers temporarily to avoid function dependency issues
ALTER TABLE user_profiles DISABLE TRIGGER audit_user_profiles;
ALTER TABLE devices DISABLE TRIGGER audit_devices;
ALTER TABLE products DISABLE TRIGGER audit_products;
ALTER TABLE orders DISABLE TRIGGER audit_orders;
ALTER TABLE meals DISABLE TRIGGER audit_meals;
ALTER TABLE reservations DISABLE TRIGGER audit_reservations;

-- Insert default admin user (this would be created through auth in production)
-- For development, we'll create a test admin user
INSERT INTO users (id, email, email_verified) VALUES
('00000000-0000-0000-0000-000000000001', 'admin@vitachain.ma', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_profiles (id, user_id, first_name, last_name, role, is_active, approved_at) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'System', 'Administrator', 'admin', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample farmers
INSERT INTO users (id, email, email_verified) VALUES
('00000000-0000-0000-0000-000000000002', 'farmer1@vitachain.ma', true),
('00000000-0000-0000-0000-000000000003', 'farmer2@vitachain.ma', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_profiles (id, user_id, first_name, last_name, role, is_active, approved_at) VALUES
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', 'Ahmed', 'Bennani', 'farmer', true, NOW()),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000003', 'Fatima', 'Alami', 'farmer', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample restaurants
INSERT INTO users (id, email, email_verified) VALUES
('00000000-0000-0000-0000-000000000004', 'restaurant1@vitachain.ma', true),
('00000000-0000-0000-0000-000000000005', 'restaurant2@vitachain.ma', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_profiles (id, user_id, first_name, last_name, role, is_active, approved_at) VALUES
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000004', 'Restaurant', 'Marrakech', 'restaurant', true, NOW()),
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000005', 'Café', 'Casablanca', 'restaurant', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample citizens
INSERT INTO users (id, email, email_verified) VALUES
('00000000-0000-0000-0000-000000000006', 'citizen1@vitachain.ma', true),
('00000000-0000-0000-0000-000000000007', 'citizen2@vitachain.ma', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_profiles (id, user_id, first_name, last_name, role, is_active, approved_at) VALUES
('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000006', 'Youssef', 'Karim', 'citizen', true, NOW()),
('00000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000007', 'Amina', 'Said', 'citizen', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample devices for farmers
INSERT INTO devices (id, user_id, name, type, status, location_lat, location_lng, api_key, configuration) VALUES
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000002', 'Greenhouse Sensor 1', 'esp32', 'active', 31.7917, -7.0926, 'test_api_key_1', '{"interval": 300, "sensors": ["temperature", "humidity", "soil_moisture"]}'),
('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000002', 'Field Sensor 1', 'esp32', 'active', 31.7917, -7.0926, 'test_api_key_2', '{"interval": 600, "sensors": ["temperature", "soil_moisture", "light"]}'),
('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000003', 'Greenhouse Sensor 2', 'esp32', 'active', 33.9716, -6.8428, 'test_api_key_3', '{"interval": 300, "sensors": ["temperature", "humidity", "soil_moisture"]}')
ON CONFLICT (id) DO NOTHING;

-- Insert sensors for devices
INSERT INTO sensors (id, device_id, type, unit, calibration_offset, min_value, max_value) VALUES
('00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000010', 'temperature', 'celsius', 0.0, -10.0, 60.0),
('00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000010', 'humidity', 'percentage', 0.0, 0.0, 100.0),
('00000000-0000-0000-0000-000000000022', '00000000-0000-0000-0000-000000000010', 'soil_moisture', 'percentage', 0.0, 0.0, 100.0),
('00000000-0000-0000-0000-000000000023', '00000000-0000-0000-0000-000000000011', 'temperature', 'celsius', 0.0, -10.0, 60.0),
('00000000-0000-0000-0000-000000000024', '00000000-0000-0000-0000-000000000011', 'soil_moisture', 'percentage', 0.0, 0.0, 100.0),
('00000000-0000-0000-0000-000000000025', '00000000-0000-0000-0000-000000000011', 'light', 'lux', 0.0, 0.0, 100000.0),
('00000000-0000-0000-0000-000000000026', '00000000-0000-0000-0000-000000000012', 'temperature', 'celsius', 0.0, -10.0, 60.0),
('00000000-0000-0000-0000-000000000027', '00000000-0000-0000-0000-000000000012', 'humidity', 'percentage', 0.0, 0.0, 100.0),
('00000000-0000-0000-0000-000000000028', '00000000-0000-0000-0000-000000000012', 'soil_moisture', 'percentage', 0.0, 0.0, 100.0)
ON CONFLICT (id) DO NOTHING;

-- Insert sample telemetry data
INSERT INTO telemetry (device_id, sensor_id, sensor_type, value, unit, quality_score) VALUES
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000020', 'temperature', 25.5, 'celsius', 0.95),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000021', 'humidity', 65.2, 'percentage', 0.92),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000022', 'soil_moisture', 45.8, 'percentage', 0.88),
('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000023', 'temperature', 28.1, 'celsius', 0.96),
('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000024', 'soil_moisture', 38.4, 'percentage', 0.90),
('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000025', 'light', 45000.0, 'lux', 0.94),
('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000026', 'temperature', 24.8, 'celsius', 0.93),
('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000027', 'humidity', 70.1, 'percentage', 0.91),
('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000028', 'soil_moisture', 52.3, 'percentage', 0.89)
ON CONFLICT DO NOTHING;

-- Insert sample products
INSERT INTO products (id, farmer_id, name, description, category, price, quantity, unit, location_lat, location_lng, is_organic, certification, harvest_date, expiry_date) VALUES
('00000000-0000-0000-0000-000000000030', '00000000-0000-0000-0000-000000000002', 'Tomatoes', 'Fresh organic tomatoes from greenhouse', 'vegetables', 12.50, 100.0, 'kg', 31.7917, -7.0926, true, 'Organic Certified', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE + INTERVAL '7 days'),
('00000000-0000-0000-0000-000000000031', '00000000-0000-0000-0000-000000000002', 'Cucumbers', 'Fresh cucumbers, perfect for salads', 'vegetables', 8.75, 50.0, 'kg', 31.7917, -7.0926, false, NULL, CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE + INTERVAL '5 days'),
('00000000-0000-0000-0000-000000000032', '00000000-0000-0000-0000-000000000003', 'Lettuce', 'Crispy lettuce leaves', 'vegetables', 15.00, 30.0, 'kg', 33.9716, -6.8428, true, 'Bio Certified', CURRENT_DATE, CURRENT_DATE + INTERVAL '4 days'),
('00000000-0000-0000-0000-000000000033', '00000000-0000-0000-0000-000000000003', 'Carrots', 'Sweet and crunchy carrots', 'vegetables', 10.00, 75.0, 'kg', 33.9716, -6.8428, false, NULL, CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '10 days')
ON CONFLICT (id) DO NOTHING;

-- Insert sample meals
INSERT INTO meals (id, restaurant_id, name, description, cuisine_type, original_price, discount_price, available_quantity, pickup_start_time, pickup_end_time, allergens, dietary_info) VALUES
('00000000-0000-0000-0000-000000000040', '00000000-0000-0000-0000-000000000004', 'Tagine with Vegetables', 'Traditional Moroccan tagine with fresh vegetables', 'moroccan', 80.00, 40.00, 8, NOW() + INTERVAL '2 hours', NOW() + INTERVAL '6 hours', '["gluten"]', '["vegetarian", "halal"]'),
('00000000-0000-0000-0000-000000000041', '00000000-0000-0000-0000-000000000004', 'Chicken Couscous', 'Authentic chicken couscous with vegetables', 'moroccan', 120.00, 60.00, 6, NOW() + INTERVAL '3 hours', NOW() + INTERVAL '7 hours', '["gluten"]', '["halal"]'),
('00000000-0000-0000-0000-000000000042', '00000000-0000-0000-0000-000000000005', 'Mixed Salad Bowl', 'Fresh mixed salad with local vegetables', 'mediterranean', 60.00, 30.00, 10, NOW() + INTERVAL '1 hour', NOW() + INTERVAL '5 hours', '[]', '["vegetarian", "vegan", "gluten-free"]'),
('00000000-0000-0000-0000-000000000043', '00000000-0000-0000-0000-000000000005', 'Quinoa Bowl', 'Healthy quinoa bowl with roasted vegetables', 'healthy', 90.00, 45.00, 5, NOW() + INTERVAL '4 hours', NOW() + INTERVAL '8 hours', '[]', '["vegetarian", "vegan", "gluten-free"]')
ON CONFLICT (id) DO NOTHING;

-- Insert pickup slots for meals
INSERT INTO pickup_slots (id, meal_id, start_time, end_time, max_reservations, current_reservations) VALUES
('00000000-0000-0000-0000-000000000050', '00000000-0000-0000-0000-000000000040', NOW() + INTERVAL '2 hours', NOW() + INTERVAL '6 hours', 8, 0),
('00000000-0000-0000-0000-000000000051', '00000000-0000-0000-0000-000000000041', NOW() + INTERVAL '3 hours', NOW() + INTERVAL '7 hours', 6, 0),
('00000000-0000-0000-0000-000000000052', '00000000-0000-0000-0000-000000000042', NOW() + INTERVAL '1 hour', NOW() + INTERVAL '5 hours', 10, 0),
('00000000-0000-0000-0000-000000000053', '00000000-0000-0000-0000-000000000043', NOW() + INTERVAL '4 hours', NOW() + INTERVAL '8 hours', 5, 0)
ON CONFLICT (id) DO NOTHING;

-- Insert sample system metrics
INSERT INTO system_metrics (metric_name, value, unit, tags) VALUES
('database.total_users', 7, 'count', '{"environment": "development"}'),
('database.active_devices', 3, 'count', '{"environment": "development"}'),
('database.total_products', 4, 'count', '{"environment": "development"}'),
('database.total_meals', 4, 'count', '{"environment": "development"}'),
('system.uptime', 86400, 'seconds', '{"environment": "development"}'),
('api.requests_per_minute', 45, 'count', '{"environment": "development"}')
ON CONFLICT DO NOTHING;

-- Insert sample support tickets
INSERT INTO support_tickets (id, user_id, ticket_number, subject, description, category, priority, status) VALUES
('00000000-0000-0000-0000-000000000060', '00000000-0000-0000-0000-000000000006', 'TKT20260501001', 'Cannot complete reservation', 'I tried to reserve a meal but got an error message', 'reservations', 'medium', 'open'),
('00000000-0000-0000-0000-000000000061', '00000000-0000-0000-0000-000000000002', 'TKT20260501002', 'Device not reporting data', 'My ESP32 device stopped sending telemetry data', 'devices', 'high', 'open')
ON CONFLICT (id) DO NOTHING;

-- Insert sample alerts
INSERT INTO alerts (user_id, type, title, message, severity, metadata) VALUES
('00000000-0000-0000-0000-000000000002', 'telemetry', 'Device Offline Alert', 'Device "Greenhouse Sensor 1" has been offline for over 1 hour', 'medium', '{"device_id": "00000000-0000-0000-0000-000000000010"}'),
('00000000-0000-0000-0000-000000000006', 'system', 'Welcome to VitaChain', 'Welcome! Your account has been successfully created.', 'low', '{"welcome": true}'),
('00000000-0000-0000-0000-000000000004', 'system', 'New Order Received', 'You have received a new order for your products.', 'medium', '{"order_count": 1}')
ON CONFLICT DO NOTHING;

-- Insert sample in-app notifications
INSERT INTO in_app_notifications (user_id, title, message, type, metadata) VALUES
('00000000-0000-0000-0000-000000000006', 'Welcome to VitaChain', 'Thank you for joining VitaChain! Start exploring our marketplace.', 'info', '{"welcome": true}'),
('00000000-0000-0000-0000-000000000002', 'Device Status Update', 'Your device "Greenhouse Sensor 1" is now online and reporting data.', 'success', '{"device_id": "00000000-0000-0000-0000-000000000010"}'),
('00000000-0000-0000-0000-000000000004', 'New Order Alert', 'You have 1 new order to process.', 'order', '{"order_count": 1}')
ON CONFLICT DO NOTHING;

-- Insert sample email notifications
INSERT INTO email_notifications (user_id, subject, content, template_name, template_data, status) VALUES
('00000000-0000-0000-0000-000000000006', 'Welcome to VitaChain', 'Welcome to VitaChain! Your account has been successfully created.', 'welcome_email', '{"user_id": "00000000-0000-0000-0000-000000000006"}', 'sent'),
('00000000-0000-0000-0000-000000000002', 'Device Alert', 'Your device has reported critical temperature readings.', 'device_alert', '{"device_id": "00000000-0000-0000-0000-000000000010"}', 'pending')
ON CONFLICT DO NOTHING;

-- Create sample audit logs
INSERT INTO audit_logs (user_id, action, table_name, record_id, new_values) VALUES
('00000000-0000-0000-0000-000000000001', 'INSERT', 'users', '00000000-0000-0000-0000-000000000001', '{"id": "00000000-0000-0000-0000-000000000001", "email": "admin@vitachain.ma", "email_verified": true}'),
('00000000-0000-0000-0000-000000000002', 'INSERT', 'devices', '00000000-0000-0000-0000-000000000010', '{"id": "00000000-0000-0000-0000-000000000010", "name": "Greenhouse Sensor 1", "type": "esp32", "status": "active"}'),
('00000000-0000-0000-0000-000000000004', 'INSERT', 'meals', '00000000-0000-0000-0000-000000000040', '{"id": "00000000-0000-0000-0000-000000000040", "name": "Tagine with Vegetables", "restaurant_id": "00000000-0000-0000-0000-000000000004"}')
ON CONFLICT DO NOTHING;

-- Update sequences to start from a higher number to avoid conflicts
SELECT setval('order_seq', 1000);
SELECT setval('ticket_seq', 1000);

-- Create a function to reset all data (for testing purposes)
CREATE OR REPLACE FUNCTION reset_test_data()
RETURNS void AS $$
BEGIN
    -- Delete test data while preserving admin user
    DELETE FROM audit_logs WHERE user_id != '00000000-0000-0000-0000-000000000001';
    DELETE FROM email_notifications WHERE user_id != '00000000-0000-0000-0000-000000000001';
    DELETE FROM in_app_notifications WHERE user_id != '00000000-0000-0000-0000-000000000001';
    DELETE FROM alerts WHERE user_id != '00000000-0000-0000-0000-000000000001';
    DELETE FROM support_tickets WHERE user_id != '00000000-0000-0000-0000-000000000001';
    DELETE FROM system_metrics;
    DELETE FROM reservations;
    DELETE FROM pickup_slots;
    DELETE FROM meals;
    DELETE FROM order_items;
    DELETE FROM orders;
    DELETE FROM products;
    DELETE FROM telemetry;
    DELETE FROM sensors;
    DELETE FROM devices;
    DELETE FROM user_profiles WHERE user_id != '00000000-0000-0000-0000-000000000001';
    DELETE FROM users WHERE id != '00000000-0000-0000-0000-000000000001';
    
    -- Reset sequences
    SELECT setval('order_seq', 1000);
    SELECT setval('ticket_seq', 1000);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on reset function to service role only
GRANT EXECUTE ON FUNCTION reset_test_data() TO service_role;

-- Create a function to generate sample telemetry data for testing
CREATE OR REPLACE FUNCTION generate_sample_telemetry(device_uuid UUID, num_readings INTEGER DEFAULT 10)
RETURNS void AS $$
DECLARE
    i INTEGER;
    sensor_uuid UUID;
    sensor_type_val VARCHAR(50);
    random_value DECIMAL(15, 6);
BEGIN
    -- Get all sensors for the device
    FOR sensor_uuid, sensor_type_val IN 
        SELECT id, type FROM sensors WHERE device_id = device_uuid AND is_active = true
    LOOP
        -- Generate random readings
        FOR i IN 1..num_readings LOOP
            -- Generate realistic values based on sensor type
            CASE sensor_type_val
                WHEN 'temperature' THEN
                    random_value := 20 + (RANDOM() * 20); -- 20-40°C
                WHEN 'humidity' THEN
                    random_value := 30 + (RANDOM() * 50); -- 30-80%
                WHEN 'soil_moisture' THEN
                    random_value := 20 + (RANDOM() * 60); -- 20-80%
                WHEN 'light' THEN
                    random_value := 1000 + (RANDOM() * 50000); -- 1000-51000 lux
                ELSE
                    random_value := RANDOM() * 100; -- Default 0-100
            END CASE;
            
            INSERT INTO telemetry (device_id, sensor_id, sensor_type, value, unit, timestamp, quality_score)
            VALUES (
                device_uuid, 
                sensor_uuid, 
                sensor_type_val, 
                random_value, 
                (SELECT unit FROM sensors WHERE id = sensor_uuid),
                NOW() - (i || ' minutes')::INTERVAL,
                0.9 + (RANDOM() * 0.1) -- 0.9-1.0 quality score
            );
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on sample data generation function
GRANT EXECUTE ON FUNCTION generate_sample_telemetry(UUID, INTEGER) TO service_role;

-- Re-enable audit triggers after seed data insertion
ALTER TABLE user_profiles ENABLE TRIGGER audit_user_profiles;
ALTER TABLE devices ENABLE TRIGGER audit_devices;
ALTER TABLE products ENABLE TRIGGER audit_products;
ALTER TABLE orders ENABLE TRIGGER audit_orders;
ALTER TABLE meals ENABLE TRIGGER audit_meals;
ALTER TABLE reservations ENABLE TRIGGER audit_reservations;
