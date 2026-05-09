-- VitaChain Performance Optimization Migration
-- Migration 04: Performance Indexes
-- This migration creates optimized indexes for improved query performance

-- Migration Info
-- Description: Add performance indexes for telemetry, products, meals, and geographic queries
-- Version: 04
-- Created: 2026-05-02
-- Dependencies: Migration 01 (core schema)

-- Performance Indexes for Telemetry Data (Time-series optimization)
-- Index for device-specific telemetry queries with time ordering
CREATE INDEX IF NOT EXISTS idx_telemetry_device_time_batch 
ON telemetry (device_id, timestamp DESC);

-- Index for user-specific telemetry queries with time ordering  
CREATE INDEX IF NOT EXISTS idx_telemetry_device_user_time_batch
ON telemetry (device_id, timestamp DESC);

-- Composite index for sensor type and timestamp queries
CREATE INDEX IF NOT EXISTS idx_telemetry_sensor_type_time
ON telemetry (sensor_type, timestamp DESC);

-- Performance Indexes for Products (Marketplace optimization)
-- Composite index for active products with creation time ordering
CREATE INDEX IF NOT EXISTS idx_products_active_created_at
ON products (is_active, created_at DESC);

-- Geographic search optimization using GIST index
CREATE INDEX IF NOT EXISTS idx_products_location_gist
ON products USING GIST (POINT(location_lng, location_lat));

-- Index for farmer's products with status
CREATE INDEX IF NOT EXISTS idx_products_farmer_active
ON products (farmer_id, is_active, created_at DESC);

-- Category-based index for product filtering
CREATE INDEX IF NOT EXISTS idx_products_category_active
ON products (category, is_active, created_at DESC);

-- Performance Indexes for Meals (Restaurant marketplace optimization)
-- Composite index for meal availability and pickup time windows
CREATE INDEX IF NOT EXISTS idx_meals_active_pickup_time
ON meals (is_active, pickup_start_time, pickup_end_time);

-- Index for restaurant's active meals
CREATE INDEX IF NOT EXISTS idx_meals_restaurant_active
ON meals (restaurant_id, is_active, pickup_start_time);

-- Cuisine type index for filtering
CREATE INDEX IF NOT EXISTS idx_meals_cuisine_active
ON meals (cuisine_type, is_active, pickup_start_time);

-- Price range index for meal searches
CREATE INDEX IF NOT EXISTS idx_meals_price_active
ON meals (discount_price, is_active);

-- Performance Indexes for Orders and Reservations
-- Index for order status and creation time
CREATE INDEX IF NOT EXISTS idx_orders_status_created_at
ON orders (status, created_at DESC);

-- Index for buyer's orders with status
CREATE INDEX IF NOT EXISTS idx_orders_buyer_status
ON orders (buyer_id, status, created_at DESC);

-- Index for reservation pickup codes (fast lookup)
CREATE INDEX IF NOT EXISTS idx_reservations_pickup_code_status
ON reservations (pickup_code, status);

-- Index for meal reservations with time window
CREATE INDEX IF NOT EXISTS idx_reservations_meal_time_status
ON reservations (meal_id, pickup_confirmed_at, status);

-- Performance Indexes for User Data
-- Index for user profiles by role and status
CREATE INDEX IF NOT EXISTS idx_user_profiles_role_active
ON user_profiles (role, is_active, created_at DESC);

-- Index for device status and last seen time
CREATE INDEX IF NOT EXISTS idx_devices_status_last_seen
ON devices (status, last_seen DESC);

-- Performance Indexes for Alerts and Notifications
-- Index for user alerts with read status and time
CREATE INDEX IF NOT EXISTS idx_alerts_user_read_created
ON alerts (user_id, is_read, created_at DESC);

-- Index for notification status and creation time
CREATE INDEX IF NOT EXISTS idx_email_notifications_status_created
ON email_notifications (status, created_at DESC);

-- Performance Indexes for System Tables
-- Index for audit logs with time and action
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_created_at
ON audit_logs (action, created_at DESC);

-- Index for system metrics with name and timestamp
CREATE INDEX IF NOT EXISTS idx_system_metrics_name_timestamp
ON system_metrics (metric_name, timestamp DESC);

-- Partial index for recent support tickets
CREATE INDEX IF NOT EXISTS idx_support_tickets_status_created
ON support_tickets (status, created_at DESC);

-- Performance Indexes for Pickup Slots
-- Index for available pickup slots
CREATE INDEX IF NOT EXISTS idx_pickup_slots_meal_time_active
ON pickup_slots (meal_id, start_time, end_time);

-- Create statistics for query optimizer
-- Update table statistics for better query planning
ANALYZE telemetry;
ANALYZE products;
ANALYZE meals;
ANALYZE orders;
ANALYZE reservations;
ANALYZE user_profiles;
ANALYZE devices;
ANALYZE alerts;
ANALYZE email_notifications;
ANALYZE audit_logs;
ANALYZE system_metrics;
ANALYZE support_tickets;
ANALYZE pickup_slots;

-- Create function for monitoring index usage
CREATE OR REPLACE FUNCTION get_index_usage_stats()
RETURNS TABLE(
    schemaname TEXT,
    tablename TEXT,
    indexname TEXT,
    idx_scan BIGINT,
    idx_tup_read BIGINT,
    idx_tup_fetch BIGINT,
    last_used TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pg_stat_user_indexes.schemaname,
        pg_stat_user_indexes.relname AS tablename,
        pg_stat_user_indexes.indexrelname AS indexname,
        pg_stat_user_indexes.idx_scan,
        pg_stat_user_indexes.idx_tup_read,
        pg_stat_user_indexes.idx_tup_fetch,
        pg_stat_user_indexes.last_idx_scan AS last_used
    FROM pg_stat_user_indexes
    WHERE pg_stat_user_indexes.relname IN (
        'telemetry', 'products', 'meals', 'orders', 'reservations',
        'user_profiles', 'devices', 'alerts', 'email_notifications',
        'audit_logs', 'system_metrics', 'support_tickets', 'pickup_slots'
    )
    ORDER BY pg_stat_user_indexes.idx_scan DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function for getting slow queries
CREATE OR REPLACE FUNCTION get_slow_queries(min_duration_ms INTEGER DEFAULT 100)
RETURNS TABLE(
    query TEXT,
    calls BIGINT,
    total_time DOUBLE PRECISION,
    mean_time DOUBLE PRECISION,
    rows BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pg_stat_statements.query,
        pg_stat_statements.calls,
        pg_stat_statements.total_exec_time,
        pg_stat_statements.mean_exec_time,
        pg_stat_statements.rows
    FROM pg_stat_statements
    WHERE pg_stat_statements.mean_exec_time * 1000 > min_duration_ms
    ORDER BY pg_stat_statements.mean_exec_time DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Create function for table statistics
CREATE OR REPLACE FUNCTION get_table_stats(target_table TEXT)
RETURNS TABLE(
    table_name TEXT,
    row_count BIGINT,
    total_size_mb DOUBLE PRECISION,
    index_size_mb DOUBLE PRECISION,
    table_size_mb DOUBLE PRECISION,
    last_vacuum TIMESTAMP WITH TIME ZONE,
    last_analyze TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname || '.' || tablename AS table_name,
        n_tup_ins + n_tup_upd + n_tup_del - n_live_tup - n_dead_tup AS row_count,
        pg_total_relation_size(schemaname||'.'||tablename) / 1024.0 / 1024.0 AS total_size_mb,
        pg_indexes_size(schemaname||'.'||tablename) / 1024.0 / 1024.0 AS index_size_mb,
        pg_relation_size(schemaname||'.'||tablename) / 1024.0 / 1024.0 AS table_size_mb,
        last_vacuum,
        last_analyze
    FROM pg_stat_user_tables
    WHERE tablename = target_table;
END;
$$ LANGUAGE plpgsql;

-- Create function for executing queries with EXPLAIN ANALYZE
CREATE OR REPLACE FUNCTION execute_query(query TEXT, params JSONB DEFAULT '{}')
RETURNS TABLE(
    execution_plan JSONB,
    execution_time_ms DOUBLE PRECISION
) AS $$
DECLARE
    start_time TIMESTAMP WITH TIME ZONE;
    end_time TIMESTAMP WITH TIME ZONE;
    plan JSONB;
BEGIN
    -- Record start time
    start_time := clock_timestamp();
    
    -- Execute EXPLAIN ANALYZE
    EXECUTE 'EXPLAIN (ANALYZE, FORMAT JSON) ' || query INTO plan;
    
    -- Record end time
    end_time := clock_timestamp();
    
    -- Return results
    RETURN QUERY SELECT plan, EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION get_index_usage_stats() TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_slow_queries(INTEGER) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_table_stats(TEXT) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION execute_query(TEXT, JSONB) TO service_role;

-- Create view for performance monitoring
CREATE OR REPLACE VIEW performance_dashboard AS
SELECT 
    'index_usage' as metric_type,
    indexname as name,
    idx_scan as value,
    'index scans' as unit
FROM get_index_usage_stats()
WHERE idx_scan > 0

UNION ALL

SELECT 
    'table_size' as metric_type,
    tablename as name,
    ROUND(total_size_mb, 2) as value,
    'MB' as unit
FROM (
    SELECT 
        schemaname || '.' || relname as tablename,
        pg_total_relation_size(schemaname||'.'||relname) / 1024.0 / 1024.0 as total_size_mb
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
) table_sizes

UNION ALL

SELECT 
    'slow_queries' as metric_type,
    'count' as name,
    COUNT(*) as value,
    'queries' as unit
FROM get_slow_queries(100);

-- Grant access to performance dashboard
GRANT SELECT ON performance_dashboard TO authenticated, service_role;

-- Add comments for documentation

COMMENT ON INDEX idx_telemetry_device_time_batch IS 'Optimized index for device-specific telemetry queries with 30-day rolling window';
COMMENT ON INDEX idx_telemetry_device_user_time_batch IS 'Optimized index for device-specific telemetry queries with 30-day rolling window';
COMMENT ON INDEX idx_products_active_created_at IS 'Composite index for active products ordered by creation time';
COMMENT ON INDEX idx_products_location_gist IS 'GIST index for geographic product searches using POINT type';
COMMENT ON INDEX idx_meals_active_pickup_time IS 'Composite index for available meals with pickup time windows';
COMMENT ON INDEX idx_reservations_pickup_code_status IS 'Optimized index for pickup code validation';

-- Performance optimization completed
-- This migration will improve query performance for:
-- 1. Time-series telemetry data queries
-- 2. Geographic product searches
-- 3. Product and meal listing queries
-- 4. Order and reservation lookups
-- 5. User profile and device queries
-- 6. Alert and notification queries
-- 7. System monitoring queries
