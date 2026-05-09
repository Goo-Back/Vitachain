-- VitaChain Database Triggers
-- Migration 04: Database Triggers
-- This migration creates all the database triggers for automation and data integrity

-- Updated timestamp triggers
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sensors_updated_at
    BEFORE UPDATE ON sensors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meals_updated_at
    BEFORE UPDATE ON meals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pickup_slots_updated_at
    BEFORE UPDATE ON pickup_slots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reservations_updated_at
    BEFORE UPDATE ON reservations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_email_notifications_updated_at
    BEFORE UPDATE ON email_notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_in_app_notifications_updated_at
    BEFORE UPDATE ON in_app_notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_support_tickets_updated_at
    BEFORE UPDATE ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Audit logging triggers
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM log_audit_event(
            COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::UUID),
            TG_OP,
            TG_TABLE_NAME,
            NEW.id,
            NULL,
            row_to_json(NEW),
            inet_client_addr(),
            current_setting('request.headers')::TEXT
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        PERFORM log_audit_event(
            COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::UUID),
            TG_OP,
            TG_TABLE_NAME,
            NEW.id,
            row_to_json(OLD),
            row_to_json(NEW),
            inet_client_addr(),
            current_setting('request.headers')::TEXT
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM log_audit_event(
            COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::UUID),
            TG_OP,
            TG_TABLE_NAME,
            OLD.id,
            row_to_json(OLD),
            NULL,
            inet_client_addr(),
            current_setting('request.headers')::TEXT
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply audit triggers to critical tables
CREATE TRIGGER audit_user_profiles
    AFTER INSERT OR UPDATE OR DELETE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_devices
    AFTER INSERT OR UPDATE OR DELETE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_products
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_meals
    AFTER INSERT OR UPDATE OR DELETE ON meals
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_reservations
    AFTER INSERT OR UPDATE OR DELETE ON reservations
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- Telemetry alert trigger
CREATE OR REPLACE FUNCTION check_telemetry_thresholds()
RETURNS TRIGGER AS $$
DECLARE
    device_uuid UUID;
    user_uuid UUID;
    alert_title VARCHAR(200);
    alert_message TEXT;
BEGIN
    device_uuid := NEW.device_id;
    
    -- Get device owner
    SELECT user_id INTO user_uuid FROM devices WHERE id = device_uuid;
    
    -- Check for critical temperature readings
    IF NEW.sensor_type = 'temperature' AND (NEW.value < 5 OR NEW.value > 45) THEN
        alert_title := 'Critical Temperature Alert';
        alert_message := format('Device %s reports critical temperature: %s°C', 
                               (SELECT name FROM devices WHERE id = device_uuid), 
                               NEW.value);
        
        PERFORM create_alert(user_uuid, 'telemetry', alert_title, alert_message, 'high');
    END IF;
    
    -- Check for low battery (if battery sensor)
    IF NEW.sensor_type = 'battery' AND NEW.value < 20 THEN
        alert_title := 'Low Battery Alert';
        alert_message := format('Device %s battery level is low: %s%%', 
                               (SELECT name FROM devices WHERE id = device_uuid), 
                               NEW.value);
        
        PERFORM create_alert(user_uuid, 'telemetry', alert_title, alert_message, 'medium');
    END IF;
    
    -- Check for soil moisture issues
    IF NEW.sensor_type = 'soil_moisture' AND NEW.value < 30 THEN
        alert_title := 'Low Soil Moisture Alert';
        alert_message := format('Device %s reports low soil moisture: %s%%', 
                               (SELECT name FROM devices WHERE id = device_uuid), 
                               NEW.value);
        
        PERFORM create_alert(user_uuid, 'telemetry', alert_title, alert_message, 'medium');
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER telemetry_threshold_check
    AFTER INSERT ON telemetry
    FOR EACH ROW
    EXECUTE FUNCTION check_telemetry_thresholds();

-- Order status change trigger
CREATE OR REPLACE FUNCTION order_status_change_notification()
RETURNS TRIGGER AS $$
DECLARE
    buyer_uuid UUID;
    order_number VARCHAR(50);
    notification_title VARCHAR(200);
    notification_message TEXT;
BEGIN
    buyer_uuid := NEW.buyer_id;
    order_number := NEW.order_number;
    
    -- Send notification when order status changes
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        notification_title := format('Order %s Status Update', order_number);
        notification_message := format('Your order %s status has been updated to: %s', 
                                      order_number, NEW.status);
        
        PERFORM create_alert(buyer_uuid, 'order', notification_title, notification_message, 'medium');
        
        -- Notify farmers if order is confirmed
        IF NEW.status = 'confirmed' THEN
            INSERT INTO email_notifications (user_id, subject, content, template_name, template_data)
            SELECT oi.farmer_id, 
                   format('New Order: %s', order_number),
                   format('You have received a new order for %s x %s', p.name, oi.quantity),
                   'new_order_notification',
                   jsonb_build_object('order_id', NEW.id, 'order_item_id', oi.id)
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = NEW.id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER order_status_notification
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION order_status_change_notification();

-- Reservation status change trigger
CREATE OR REPLACE FUNCTION reservation_status_change_notification()
RETURNS TRIGGER AS $$
DECLARE
    citizen_uuid UUID;
    restaurant_uuid UUID;
    meal_name VARCHAR(200);
    pickup_code VARCHAR(6);
    notification_title VARCHAR(200);
    notification_message TEXT;
BEGIN
    citizen_uuid := NEW.citizen_id;
    pickup_code := NEW.pickup_code;
    
    -- Get meal details
    SELECT m.name, m.restaurant_id INTO meal_name, restaurant_uuid
    FROM meals m
    WHERE m.id = NEW.meal_id;
    
    -- Send notification when reservation status changes
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        notification_title := format('Reservation %s Status Update', pickup_code);
        notification_message := format('Your reservation for "%s" (Code: %s) status is now: %s', 
                                      meal_name, pickup_code, NEW.status);
        
        PERFORM create_alert(citizen_uuid, 'reservation', notification_title, notification_message, 'medium');
        
        -- Send pickup code when reservation is confirmed
        IF NEW.status = 'confirmed' THEN
            INSERT INTO email_notifications (user_id, subject, content, template_name, template_data)
            VALUES (citizen_uuid, 
                   format('Pickup Code: %s', pickup_code),
                   format('Your reservation for "%s" is confirmed. Pickup code: %s', meal_name, pickup_code),
                   'pickup_code_notification',
                   jsonb_build_object('reservation_id', NEW.id, 'pickup_code', pickup_code));
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER reservation_status_notification
    AFTER UPDATE ON reservations
    FOR EACH ROW
    EXECUTE FUNCTION reservation_status_change_notification();

-- Device offline alert trigger
CREATE OR REPLACE FUNCTION check_device_offline()
RETURNS TRIGGER AS $$
DECLARE
    device_uuid UUID;
    user_uuid UUID;
    device_name VARCHAR(100);
BEGIN
    device_uuid := NEW.id;
    user_uuid := NEW.user_id;
    device_name := NEW.name;
    
    -- Check if device hasn't been seen for more than 1 hour
    IF NEW.last_seen < NOW() - INTERVAL '1 hour' AND NEW.status = 'active' THEN
        PERFORM create_alert(
            user_uuid, 
            'system', 
            'Device Offline Alert',
            format('Device "%s" has been offline for over 1 hour', device_name),
            'medium',
            jsonb_build_object('device_id', device_uuid, 'last_seen', NEW.last_seen)
        );
        
        -- Update device status to inactive
        UPDATE devices 
        SET status = 'inactive' 
        WHERE id = device_uuid;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER device_offline_check
    AFTER UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION check_device_offline();

-- Meal expiration trigger
CREATE OR REPLACE FUNCTION check_meal_expiration()
RETURNS TRIGGER AS $$
DECLARE
    restaurant_uuid UUID;
    meal_name VARCHAR(200);
BEGIN
    -- If meal pickup time has passed and meal is still active
    IF NEW.pickup_end_time < NOW() AND NEW.is_active = true THEN
        restaurant_uuid := NEW.restaurant_id;
        meal_name := NEW.name;
        
        -- Notify restaurant about expired meal
        PERFORM create_alert(
            restaurant_uuid,
            'system',
            'Meal Expired',
            format('Meal "%s" pickup time has expired', meal_name),
            'medium',
            jsonb_build_object('meal_id', NEW.id)
        );
        
        -- Update meal status
        UPDATE meals 
        SET is_active = false 
        WHERE id = NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER meal_expiration_check
    AFTER UPDATE ON meals
    FOR EACH ROW
    EXECUTE FUNCTION check_meal_expiration();

-- Reservation expiration trigger
CREATE OR REPLACE FUNCTION check_reservation_expiration()
RETURNS TRIGGER AS $$
DECLARE
    citizen_uuid UUID;
    meal_name VARCHAR(200);
    pickup_code VARCHAR(6);
BEGIN
    -- If reservation pickup time has passed and status is still pending/confirmed
    IF NEW.pickup_end_time < NOW() AND NEW.status IN ('pending', 'confirmed') THEN
        citizen_uuid := NEW.citizen_id;
        pickup_code := NEW.pickup_code;
        
        -- Get meal name
        SELECT m.name INTO meal_name
        FROM meals m
        WHERE m.id = NEW.meal_id;
        
        -- Notify citizen about expired reservation
        PERFORM create_alert(
            citizen_uuid,
            'reservation',
            'Reservation Expired',
            format('Your reservation for "%s" (Code: %s) has expired', meal_name, pickup_code),
            'medium',
            jsonb_build_object('reservation_id', NEW.id, 'pickup_code', pickup_code)
        );
        
        -- Update reservation status
        UPDATE reservations 
        SET status = 'expired',
            cancelled_at = NOW(),
            cancellation_reason = 'Pickup time expired'
        WHERE id = NEW.id;
        
        -- Restore meal quantity
        UPDATE meals
        SET available_quantity = available_quantity + NEW.quantity
        WHERE id = NEW.meal_id;
        
        -- Update pickup slot
        UPDATE pickup_slots
        SET current_reservations = current_reservations - 1
        WHERE id = NEW.pickup_slot_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER reservation_expiration_check
    AFTER UPDATE ON reservations
    FOR EACH ROW
    EXECUTE FUNCTION check_reservation_expiration();

-- System metrics recording trigger
CREATE OR REPLACE FUNCTION record_system_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Record database size metrics
    PERFORM record_metric('database.total_tables', 
                          (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'), 
                          'count');
    
    PERFORM record_metric('database.total_users', 
                          (SELECT COUNT(*) FROM users), 
                          'count');
    
    PERFORM record_metric('database.active_devices', 
                          (SELECT COUNT(*) FROM devices WHERE status = 'active'), 
                          'count');
    
    PERFORM record_metric('database.pending_orders', 
                          (SELECT COUNT(*) FROM orders WHERE status = 'pending'), 
                          'count');
    
    PERFORM record_metric('database.active_reservations', 
                          (SELECT COUNT(*) FROM reservations WHERE status IN ('pending', 'confirmed')), 
                          'count');
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a scheduled function for metrics (would need pg_cron extension)
-- For now, we'll create a manual trigger function

-- Data validation trigger for products
CREATE OR REPLACE FUNCTION validate_product_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Validate price is positive
    IF NEW.price <= 0 THEN
        RAISE EXCEPTION 'Product price must be positive';
    END IF;
    
    -- Validate quantity is positive
    IF NEW.quantity <= 0 THEN
        RAISE EXCEPTION 'Product quantity must be positive';
    END IF;
    
    -- Validate expiry date is after harvest date
    IF NEW.harvest_date IS NOT NULL AND NEW.expiry_date IS NOT NULL THEN
        IF NEW.expiry_date <= NEW.harvest_date THEN
            RAISE EXCEPTION 'Expiry date must be after harvest date';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER validate_product_data_trigger
    BEFORE INSERT OR UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION validate_product_data();

-- Data validation trigger for meals
CREATE OR REPLACE FUNCTION validate_meal_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Validate prices are positive
    IF NEW.original_price <= 0 OR NEW.discount_price <= 0 THEN
        RAISE EXCEPTION 'Meal prices must be positive';
    END IF;
    
    -- Validate discount price is less than original price
    IF NEW.discount_price >= NEW.original_price THEN
        RAISE EXCEPTION 'Discount price must be less than original price';
    END IF;
    
    -- Validate pickup times
    IF NEW.pickup_end_time <= NEW.pickup_start_time THEN
        RAISE EXCEPTION 'Pickup end time must be after start time';
    END IF;
    
    -- Validate pickup start time is in the future
    IF NEW.pickup_start_time <= NOW() THEN
        RAISE EXCEPTION 'Pickup start time must be in the future';
    END IF;
    
    -- Validate available quantity is positive
    IF NEW.available_quantity <= 0 THEN
        RAISE EXCEPTION 'Available quantity must be positive';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER validate_meal_data_trigger
    BEFORE INSERT OR UPDATE ON meals
    FOR EACH ROW
    EXECUTE FUNCTION validate_meal_data();

-- Email notification retry logic trigger
CREATE OR REPLACE FUNCTION handle_email_notification_retry()
RETURNS TRIGGER AS $$
DECLARE
    max_retries INTEGER := 3;
BEGIN
    -- If notification failed and retry count is below max
    IF NEW.status = 'failed' AND NEW.retry_count < max_retries THEN
        -- Reset status to pending for retry
        NEW.status = 'pending';
        NEW.retry_count = NEW.retry_count + 1;
    ELSIF NEW.status = 'failed' AND NEW.retry_count >= max_retries THEN
        -- Log metric for failed notifications
        PERFORM record_metric('email_notifications.failed_max_retries', 1, 'count');
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER email_notification_retry_trigger
    BEFORE UPDATE ON email_notifications
    FOR EACH ROW
    EXECUTE FUNCTION handle_email_notification_retry();
