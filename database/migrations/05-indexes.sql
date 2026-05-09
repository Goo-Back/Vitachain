-- VitaChain Database Performance Optimization
-- Migration 05: Advanced Indexes and Performance Optimization
-- This migration creates additional indexes for optimal query performance

-- Time-series telemetry optimization
CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp ON telemetry(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_device_sensor_timestamp ON telemetry(device_id, sensor_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp_value ON telemetry(timestamp, value);

-- Location-based indexes for queries
CREATE INDEX IF NOT EXISTS idx_devices_location ON devices(location_lat, location_lng) WHERE location_lat IS NOT NULL AND location_lng IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_location ON products(location_lat, location_lng) WHERE location_lat IS NOT NULL AND location_lng IS NOT NULL;

-- Product search optimization
CREATE INDEX IF NOT EXISTS idx_products_search ON products(name) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_products_category_price ON products(category, price) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_products_farmer_active ON products(farmer_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_products_quantity_available ON products(quantity DESC) WHERE is_active = true AND quantity > 0;

-- Order optimization
CREATE INDEX IF NOT EXISTS idx_orders_buyer_status_created ON orders(buyer_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status_created ON orders(status, created_at DESC) WHERE status IN ('pending', 'confirmed');
CREATE INDEX IF NOT EXISTS idx_orders_delivery_date ON orders(delivery_date);
CREATE INDEX IF NOT EXISTS idx_orders_total_amount ON orders(total_amount DESC) WHERE status != 'cancelled';

-- Order items optimization
CREATE INDEX IF NOT EXISTS idx_order_items_farmer_status ON order_items(farmer_id, order_id, quantity, total_price);
CREATE INDEX IF NOT EXISTS idx_order_items_product_quantity ON order_items(product_id, quantity, unit_price);

-- Meal search optimization
CREATE INDEX IF NOT EXISTS idx_meals_search ON meals(name) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_meals_restaurant_active ON meals(restaurant_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_meals_pickup_time ON meals(pickup_start_time, pickup_end_time) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_meals_discount_price ON meals(discount_price ASC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_meals_cuisine_type ON meals(cuisine_type) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_meals_quantity_available ON meals(available_quantity DESC) WHERE is_active = true AND available_quantity > 0;

-- Pickup slots optimization
CREATE INDEX IF NOT EXISTS idx_pickup_slots_meal_time_active ON pickup_slots(meal_id, start_time, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_pickup_slots_capacity ON pickup_slots(max_reservations, current_reservations) WHERE is_active = true AND current_reservations < max_reservations;

-- Reservations optimization
CREATE INDEX IF NOT EXISTS idx_reservations_meal_status ON reservations(meal_id, status) WHERE status IN ('pending', 'confirmed');
CREATE INDEX IF NOT EXISTS idx_reservations_citizen_status ON reservations(citizen_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reservations_pickup_time ON reservations(reserved_at) WHERE status IN ('pending', 'confirmed');
CREATE INDEX IF NOT EXISTS idx_reservations_meal_citizen ON reservations(meal_id, citizen_id);

-- Alerts optimization
CREATE INDEX IF NOT EXISTS idx_alerts_user_unread ON alerts(user_id, is_read, created_at DESC) WHERE is_read = false;
CREATE INDEX IF NOT EXISTS idx_alerts_type_created ON alerts(type, created_at DESC) ;
CREATE INDEX IF NOT EXISTS idx_alerts_expires ON alerts(expires_at) WHERE expires_at IS NOT NULL;

-- Notifications optimization
CREATE INDEX IF NOT EXISTS idx_email_notifications_status_created ON email_notifications(status, created_at DESC) WHERE status IN ('pending', 'failed');
CREATE INDEX IF NOT EXISTS idx_in_app_notifications_user_unread ON in_app_notifications(user_id, is_read, created_at DESC) WHERE is_read = false;
CREATE INDEX IF NOT EXISTS idx_in_app_notifications_expires ON in_app_notifications(expires_at) WHERE expires_at IS NOT NULL;

-- Audit logs optimization
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action_created ON audit_logs(user_id, action, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_created ON audit_logs(table_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_created ON audit_logs(action, created_at DESC);

-- System metrics optimization
CREATE INDEX IF NOT EXISTS idx_system_metrics_name_timestamp ON system_metrics(metric_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

-- Support tickets optimization
CREATE INDEX IF NOT EXISTS idx_support_tickets_user_status ON support_tickets(user_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status_priority ON support_tickets(status, priority) WHERE status IN ('open', 'in_progress');
CREATE INDEX IF NOT EXISTS idx_support_tickets_assigned_status ON support_tickets(assigned_to, status) WHERE assigned_to IS NOT NULL;

-- User profiles optimization
CREATE INDEX IF NOT EXISTS idx_user_profiles_role_active ON user_profiles(role, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_user_profiles_approved ON user_profiles(approved_at) WHERE approved_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_profiles_name_search ON user_profiles(first_name, last_name);

-- Devices optimization
CREATE INDEX IF NOT EXISTS idx_devices_user_status ON devices(user_id, status) WHERE status IN ('active', 'inactive');
CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_devices_type_status ON devices(type, status) WHERE status = 'active';

-- Sensors optimization
CREATE INDEX IF NOT EXISTS idx_sensors_device_type_active ON sensors(device_id, type) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_sensors_type_active ON sensors(type, is_active) WHERE is_active = true;

-- Telemetry advanced optimization for analytics
CREATE INDEX IF NOT EXISTS idx_telemetry_analytics ON telemetry(device_id, sensor_type, timestamp DESC, value, quality_score);

-- Partial indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_products_active_organic ON products(is_organic, created_at DESC) WHERE is_active = true AND is_organic = true;
CREATE INDEX IF NOT EXISTS idx_meals_discount_high ON meals(discount_percentage DESC, created_at DESC) WHERE is_active = true AND discount_percentage >= 50;
CREATE INDEX IF NOT EXISTS idx_reservations_pending_pickup ON reservations(reserved_at, created_at DESC) WHERE status = 'pending';

-- Composite indexes for complex queries
CREATE INDEX IF NOT EXISTS idx_orders_composite ON orders(buyer_id, status, created_at DESC, total_amount, order_number);
CREATE INDEX IF NOT EXISTS idx_reservations_composite ON reservations(citizen_id, status, reserved_at, created_at DESC, pickup_code, total_amount);

-- Create functional indexes for computed values
CREATE INDEX IF NOT EXISTS idx_meals_discount_amount ON meals(original_price, discount_price) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_products_price_per_unit ON products(price, quantity) WHERE is_active = true;

-- Create indexes for JSONB queries
CREATE INDEX IF NOT EXISTS idx_devices_config_gin ON devices USING gin(configuration) WHERE configuration IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_telemetry_metadata_gin ON telemetry USING gin(metadata) WHERE metadata IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_alerts_metadata_gin ON alerts USING gin(metadata) WHERE metadata IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_images_gin ON products USING gin(images) WHERE images IS NOT NULL AND jsonb_array_length(images) > 0;
CREATE INDEX IF NOT EXISTS idx_meals_images_gin ON meals USING gin(images) WHERE images IS NOT NULL AND jsonb_array_length(images) > 0;

-- Create expression indexes for common conditions
CREATE INDEX IF NOT EXISTS idx_meals_pickup_today ON meals(pickup_start_time, pickup_end_time) 
    WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_orders_pending_delivery ON orders(delivery_date, status) 
    WHERE status = 'confirmed';

-- Create covering indexes for frequent queries
CREATE INDEX IF NOT EXISTS idx_products_covering ON products(id, farmer_id, name, price, quantity, is_active, created_at) 
    WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_meals_covering ON meals(id, restaurant_id, name, discount_price, available_quantity, pickup_start_time, pickup_end_time, is_active) 
    WHERE is_active = true;

-- Create indexes for foreign key constraints (if not already created)
CREATE INDEX IF NOT EXISTS fk_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS fk_devices_user_id ON devices(user_id);
CREATE INDEX IF NOT EXISTS fk_sensors_device_id ON sensors(device_id);
CREATE INDEX IF NOT EXISTS fk_telemetry_device_id ON telemetry(device_id);
CREATE INDEX IF NOT EXISTS fk_products_farmer_id ON products(farmer_id);
CREATE INDEX IF NOT EXISTS fk_orders_buyer_id ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS fk_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS fk_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS fk_meals_restaurant_id ON meals(restaurant_id);
CREATE INDEX IF NOT EXISTS fk_pickup_slots_meal_id ON pickup_slots(meal_id);
CREATE INDEX IF NOT EXISTS fk_reservations_meal_id ON reservations(meal_id);
CREATE INDEX IF NOT EXISTS fk_reservations_citizen_id ON reservations(citizen_id);
CREATE INDEX IF NOT EXISTS fk_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS fk_email_notifications_user_id ON email_notifications(user_id);
CREATE INDEX IF NOT EXISTS fk_in_app_notifications_user_id ON in_app_notifications(user_id);
CREATE INDEX IF NOT EXISTS fk_support_tickets_user_id ON support_tickets(user_id);

-- Create statistics collection for query optimization
ALTER TABLE telemetry ALTER COLUMN timestamp SET STATISTICS 1000;
ALTER TABLE orders ALTER COLUMN created_at SET STATISTICS 1000;
ALTER TABLE reservations ALTER COLUMN created_at SET STATISTICS 1000;
ALTER TABLE system_metrics ALTER COLUMN timestamp SET STATISTICS 1000;

-- Create table statistics for better query planning
ANALYZE users;
ANALYZE user_profiles;
ANALYZE devices;
ANALYZE sensors;
ANALYZE telemetry;
ANALYZE products;
ANALYZE orders;
ANALYZE order_items;
ANALYZE meals;
ANALYZE pickup_slots;
ANALYZE reservations;
ANALYZE alerts;
ANALYZE email_notifications;
ANALYZE in_app_notifications;
ANALYZE audit_logs;
ANALYZE system_metrics;
ANALYZE support_tickets;

-- Create index usage monitoring view
CREATE OR REPLACE VIEW index_usage_stats AS
SELECT 
    schemaname,
    relname AS tablename,
    indexrelname AS indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Grant access to index usage view for monitoring
GRANT SELECT ON index_usage_stats TO authenticated;

-- Create simple query monitoring view (pg_stat_statements not available in Supabase)
CREATE OR REPLACE VIEW slow_queries AS
SELECT 
    'Query monitoring not available in Supabase' AS note,
    NOW() AS checked_at
LIMIT 1;

-- Grant access to slow queries view for monitoring
GRANT SELECT ON slow_queries TO authenticated;

-- Create table size monitoring view
CREATE OR REPLACE VIEW table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Grant access to table sizes view for monitoring
GRANT SELECT ON table_sizes TO authenticated;
