-- VitaChain Database Functions
-- Migration 03: Database Functions
-- This migration creates all the database functions for business logic

-- Timestamp update function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- User management functions
CREATE OR REPLACE FUNCTION create_user_profile(
    user_uuid UUID,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20) DEFAULT NULL,
    role user_role DEFAULT 'citizen'
)
RETURNS UUID AS $$
DECLAREcd 
    profile_id UUID;
BEGIN
    INSERT INTO user_profiles (user_id, first_name, last_name, phone, role)
    VALUES (user_uuid, first_name, last_name, phone, role)
    RETURNING id INTO profile_id;
    
    RETURN profile_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION approve_user_profile(
    profile_uuid UUID,
    admin_uuid UUID
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE user_profiles 
    SET approved_at = NOW(),
        approved_by = admin_uuid
    WHERE id = profile_uuid;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Device management functions
CREATE OR REPLACE FUNCTION register_device(
    user_uuid UUID,
    device_name VARCHAR(100),
    device_type device_type DEFAULT 'esp32',
    location_lat DECIMAL(10, 8) DEFAULT NULL,
    location_lng DECIMAL(11, 8) DEFAULT NULL,
    configuration JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    device_uuid UUID;
    api_key VARCHAR(255);
BEGIN
    -- Generate unique API key
    api_key := encode(sha256(device_uuid || device_name || NOW()::text), 'hex');
    
    INSERT INTO devices (user_id, name, type, location_lat, location_lng, api_key, configuration)
    VALUES (user_uuid, device_name, device_type, location_lat, location_lng, api_key, configuration)
    RETURNING id INTO device_uuid;
    
    RETURN device_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION update_device_last_seen(
    device_uuid UUID
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE devices 
    SET last_seen = NOW()
    WHERE id = device_uuid;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Telemetry ingestion function
CREATE OR REPLACE FUNCTION ingest_telemetry(
    device_uuid UUID,
    sensor_type VARCHAR(50),
    value DECIMAL(15, 6),
    unit VARCHAR(20) DEFAULT NULL,
    quality_score DECIMAL(3, 2) DEFAULT 1.0,
    metadata JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    telemetry_uuid UUID;
    sensor_uuid UUID;
BEGIN
    -- Find or create sensor
    SELECT id INTO sensor_uuid 
    FROM sensors 
    WHERE device_id = device_uuid AND type = sensor_type AND is_active = true;
    
    IF sensor_uuid IS NULL THEN
        -- Create new sensor if not found
        INSERT INTO sensors (device_id, type, unit)
        VALUES (device_uuid, sensor_type, unit)
        RETURNING id INTO sensor_uuid;
    END IF;
    
    -- Insert telemetry data
    INSERT INTO telemetry (device_id, sensor_id, sensor_type, value, unit, quality_score, metadata)
    VALUES (device_uuid, sensor_uuid, sensor_type, value, unit, quality_score, metadata)
    RETURNING id INTO telemetry_uuid;
    
    -- Update device last seen
    PERFORM update_device_last_seen(device_uuid);
    
    RETURN telemetry_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Product management functions
CREATE OR REPLACE FUNCTION create_product(
    farmer_uuid UUID,
    product_name VARCHAR(200),
    description TEXT,
    category VARCHAR(50),
    price DECIMAL(10, 2),
    quantity DECIMAL(10, 2),
    unit VARCHAR(20),
    location_lat DECIMAL(10, 8) DEFAULT NULL,
    location_lng DECIMAL(11, 8) DEFAULT NULL,
    is_organic BOOLEAN DEFAULT FALSE,
    certification VARCHAR(100) DEFAULT NULL,
    harvest_date DATE DEFAULT NULL,
    expiry_date DATE DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    product_uuid UUID;
BEGIN
    INSERT INTO products (
        farmer_id, name, description, category, price, quantity, unit,
        location_lat, location_lng, is_organic, certification, harvest_date, expiry_date
    )
    VALUES (
        farmer_uuid, product_name, description, category, price, quantity, unit,
        location_lat, location_lng, is_organic, certification, harvest_date, expiry_date
    )
    RETURNING id INTO product_uuid;
    
    RETURN product_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Order management functions
CREATE OR REPLACE FUNCTION create_order(
    buyer_uuid UUID,
    items JSONB, -- Array of {product_id, quantity}
    delivery_address TEXT,
    delivery_date DATE,
    notes TEXT
)
RETURNS UUID AS $$
DECLARE
    order_uuid UUID;
    order_number VARCHAR(50);
    total_amount DECIMAL(10, 2);
    item JSONB;
    product_uuid UUID;
    item_quantity DECIMAL(10, 2);
    unit_price DECIMAL(10, 2);
    farmer_uuid UUID;
BEGIN
    -- Generate order number
    order_number := 'ORD' || TO_CHAR(NOW(), 'YYYYMMDD') || LPAD(NEXTVAL('order_seq')::text, 4, '0');
    
    -- Calculate total amount and validate items
    total_amount := 0;
    FOR item IN SELECT * FROM jsonb_array_elements(items)
    LOOP
        product_uuid := (item->>'product_id')::UUID;
        item_quantity := (item->>'quantity')::DECIMAL(10, 2);
        
        -- Get product price and farmer
        SELECT price, farmer_id INTO unit_price, farmer_uuid
        FROM products
        WHERE id = product_uuid AND is_active = true;
        
        IF unit_price IS NULL THEN
            RAISE EXCEPTION 'Product % not found or inactive', product_uuid;
        END IF;
        
        total_amount := total_amount + (unit_price * item_quantity);
    END LOOP;
    
    -- Create order
    INSERT INTO orders (buyer_id, order_number, total_amount, delivery_address, delivery_date, notes)
    VALUES (buyer_uuid, order_number, total_amount, delivery_address, delivery_date, notes)
    RETURNING id INTO order_uuid;
    
    -- Create order items
    FOR item IN SELECT * FROM jsonb_array_elements(items)
    LOOP
        product_uuid := (item->>'product_id')::UUID;
        item_quantity := (item->>'quantity')::DECIMAL(10, 2);
        
        -- Get product details
        SELECT price, farmer_id INTO unit_price, farmer_uuid
        FROM products
        WHERE id = product_uuid;
        
        INSERT INTO order_items (order_id, product_id, farmer_id, quantity, unit_price, total_price)
        VALUES (order_uuid, product_uuid, farmer_uuid, item_quantity, unit_price, unit_price * item_quantity);
        
        -- Update product quantity
        UPDATE products
        SET quantity = quantity - item_quantity
        WHERE id = product_uuid;
    END LOOP;
    
    RETURN order_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Meal management functions
CREATE OR REPLACE FUNCTION create_meal(
    restaurant_uuid UUID,
    meal_name VARCHAR(200),
    description TEXT,
    cuisine_type VARCHAR(50),
    original_price DECIMAL(10, 2),
    discount_price DECIMAL(10, 2),
    available_quantity INTEGER,
    pickup_start_time TIMESTAMP WITH TIME ZONE,
    pickup_end_time TIMESTAMP WITH TIME ZONE,
    allergens JSONB DEFAULT '[]',
    dietary_info JSONB DEFAULT '[]',
    preparation_instructions TEXT DEFAULT NULL,
    storage_instructions TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    meal_uuid UUID;
BEGIN
    INSERT INTO meals (
        restaurant_id, name, description, cuisine_type, original_price, discount_price,
        available_quantity, pickup_start_time, pickup_end_time, allergens, dietary_info,
        preparation_instructions, storage_instructions
    )
    VALUES (
        restaurant_uuid, meal_name, description, cuisine_type, original_price, discount_price,
        available_quantity, pickup_start_time, pickup_end_time, allergens, dietary_info,
        preparation_instructions, storage_instructions
    )
    RETURNING id INTO meal_uuid;
    
    -- Create pickup slots
    INSERT INTO pickup_slots (meal_id, start_time, end_time, max_reservations)
    VALUES (meal_uuid, pickup_start_time, pickup_end_time, available_quantity);
    
    RETURN meal_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Reservation management functions
CREATE OR REPLACE FUNCTION create_reservation(
    meal_uuid UUID,
    citizen_uuid UUID,
    quantity INTEGER DEFAULT 1
)
RETURNS UUID AS $$
DECLARE
    reservation_uuid UUID;
    pickup_code VARCHAR(6);
    meal_available INTEGER;
    total_amount DECIMAL(10, 2);
    pickup_slot_uuid UUID;
BEGIN
    -- Check meal availability
    SELECT available_quantity, discount_price INTO meal_available, total_amount
    FROM meals
    WHERE id = meal_uuid AND is_active = true AND pickup_end_time > NOW();
    
    IF meal_available IS NULL THEN
        RAISE EXCEPTION 'Meal not available or expired';
    END IF;
    
    IF meal_available < quantity THEN
        RAISE EXCEPTION 'Insufficient quantity available';
    END IF;
    
    -- Generate unique pickup code
    pickup_code := LPAD((RANDOM() * 1000000)::INTEGER::text, 6, '0');
    
    -- Get pickup slot
    SELECT id INTO pickup_slot_uuid
    FROM pickup_slots
    WHERE meal_id = meal_uuid AND is_active = true
    LIMIT 1;
    
    -- Create reservation
    INSERT INTO reservations (meal_id, pickup_slot_id, citizen_id, quantity, pickup_code, total_amount)
    VALUES (meal_uuid, pickup_slot_uuid, citizen_uuid, quantity, pickup_code, total_amount * quantity)
    RETURNING id INTO reservation_uuid;
    
    -- Update meal quantity
    UPDATE meals
    SET available_quantity = available_quantity - quantity
    WHERE id = meal_uuid;
    
    -- Update pickup slot reservations
    UPDATE pickup_slots
    SET current_reservations = current_reservations + 1
    WHERE id = pickup_slot_uuid;
    
    RETURN reservation_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION confirm_pickup(
    pickup_code VARCHAR(6)
)
RETURNS BOOLEAN AS $$
DECLARE
    reservation_uuid UUID;
    meal_uuid UUID;
    pickup_slot_uuid UUID;
BEGIN
    -- Find reservation by pickup code
    SELECT id, meal_id, pickup_slot_id INTO reservation_uuid, meal_uuid, pickup_slot_uuid
    FROM reservations
    WHERE pickup_code = pickup_code 
    AND status = 'confirmed'
    AND pickup_end_time > NOW()
    LIMIT 1;
    
    IF reservation_uuid IS NULL THEN
        RETURN false;
    END IF;
    
    -- Update reservation status
    UPDATE reservations
    SET status = 'completed',
        pickup_completed_at = NOW()
    WHERE id = reservation_uuid;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Notification functions
CREATE OR REPLACE FUNCTION create_alert(
    user_uuid UUID,
    alert_type alert_type,
    title VARCHAR(200),
    message TEXT,
    severity VARCHAR(20) DEFAULT 'medium',
    metadata JSONB DEFAULT '{}',
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    alert_uuid UUID;
BEGIN
    INSERT INTO alerts (user_id, type, title, message, severity, metadata, expires_at)
    VALUES (user_uuid, alert_type, title, message, severity, metadata, expires_at)
    RETURNING id INTO alert_uuid;
    
    -- Create in-app notification
    INSERT INTO in_app_notifications (user_id, title, message, type, metadata, expires_at)
    VALUES (user_uuid, title, message, alert_type, metadata, expires_at);
    
    -- Create email notification (queue)
    INSERT INTO email_notifications (user_id, subject, content, template_name, template_data)
    VALUES (user_uuid, title, message, 'alert_notification', jsonb_build_object('alert', alert_uuid));
    
    RETURN alert_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Audit logging function
CREATE OR REPLACE FUNCTION log_audit_event(
    user_uuid UUID,
    action VARCHAR(100),
    table_name VARCHAR(50),
    record_id UUID DEFAULT NULL,
    old_values JSONB DEFAULT NULL,
    new_values JSONB DEFAULT NULL,
    ip_address INET DEFAULT NULL,
    user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    audit_uuid UUID;
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values, ip_address, user_agent)
    VALUES (user_uuid, action, table_name, record_id, old_values, new_values, ip_address, user_agent)
    RETURNING id INTO audit_uuid;
    
    RETURN audit_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- System metrics function
CREATE OR REPLACE FUNCTION record_metric(
    metric_name VARCHAR(100),
    value DECIMAL(15, 6),
    unit VARCHAR(20) DEFAULT NULL,
    tags JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    metric_uuid UUID;
BEGIN
    INSERT INTO system_metrics (metric_name, value, unit, tags)
    VALUES (metric_name, value, unit, tags)
    RETURNING id INTO metric_uuid;
    
    RETURN metric_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Support ticket function
CREATE OR REPLACE FUNCTION create_support_ticket(
    user_uuid UUID,
    subject VARCHAR(200),
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    priority VARCHAR(20) DEFAULT 'medium'
)
RETURNS UUID AS $$
DECLARE
    ticket_uuid UUID;
    ticket_number VARCHAR(50);
BEGIN
    -- Generate ticket number
    ticket_number := 'TKT' || TO_CHAR(NOW(), 'YYYYMMDD') || LPAD(NEXTVAL('ticket_seq')::text, 4, '0');
    
    INSERT INTO support_tickets (user_id, ticket_number, subject, description, category, priority)
    VALUES (user_uuid, ticket_number, subject, description, category, priority)
    RETURNING id INTO ticket_uuid;
    
    RETURN ticket_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Utility functions
CREATE OR REPLACE FUNCTION generate_pickup_code()
RETURNS VARCHAR(6) AS $$
BEGIN
    RETURN LPAD((RANDOM() * 1000000)::INTEGER::text, 6, '0');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_discount_percentage(
    original_price DECIMAL(10, 2),
    discount_price DECIMAL(10, 2)
)
RETURNS INTEGER AS $$
BEGIN
    RETURN ROUND(((original_price - discount_price) / original_price) * 100);
END;
$$ LANGUAGE plpgsql;

-- Create sequences for order numbers and ticket numbers
CREATE SEQUENCE IF NOT EXISTS order_seq START 1;
CREATE SEQUENCE IF NOT EXISTS ticket_seq START 1;

-- Grant execute permissions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated, service_role;
