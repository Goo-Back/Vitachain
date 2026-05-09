-- VitaChain Database Configuration
-- This file configures database parameters and settings for optimal performance and security

-- Configure database parameters
-- ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements, pgaudit';
-- ALTER SYSTEM SET track_activity_query_size = 2048;
-- ALTER SYSTEM SET pg_stat_statements.track = 'all';
-- ALTER SYSTEM SET pg_stat_statements.max = 10000;
-- ALTER SYSTEM SET pg_stat_statements.track_utility = true;

-- Configure connection pooling
-- ALTER SYSTEM SET max_connections = 200;
-- ALTER SYSTEM SET superuser_reserved_connections = 3;
-- ALTER SYSTEM SET shared_buffers = '256MB';
-- ALTER SYSTEM SET effective_cache_size = '1GB';
-- ALTER SYSTEM SET work_mem = '4MB';
-- ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Configure WAL settings for performance
-- ALTER SYSTEM SET wal_buffers = '16MB';
-- ALTER SYSTEM SET checkpoint_completion_target = 0.9;
-- ALTER SYSTEM SET wal_writer_delay = '200ms';
-- ALTER SYSTEM SET commit_delay = '0';
-- ALTER SYSTEM SET commit_siblings = 5;

-- Configure autovacuum for optimal performance
-- Note: ALTER SYSTEM commands are not available in Supabase
-- These settings would be configured at the database level in a self-hosted instance
-- Autovacuum is already optimally configured by Supabase by default

-- Configure logging for monitoring and debugging
-- Note: ALTER SYSTEM logging commands are not available in Supabase
-- Supabase provides its own logging and monitoring infrastructure
-- Application-level logging should be implemented instead

-- Configure timezone and locale
-- Note: ALTER SYSTEM locale commands are not available in Supabase
-- Timezone and locale are already optimally configured by Supabase
-- -- ALTER SYSTEM SET timezone = 'UTC';
-- -- ALTER SYSTEM SET lc_messages = 'en_US.UTF-8';
-- -- ALTER SYSTEM SET lc_monetary = 'en_US.UTF-8';
-- -- ALTER SYSTEM SET lc_numeric = 'en_US.UTF-8';
-- -- ALTER SYSTEM SET lc_time = 'en_US.UTF-8';

-- Configure security settings
-- Note: ALTER SYSTEM security commands are not available in Supabase
-- SSL and security are already optimally configured by Supabase
-- -- ALTER SYSTEM SET ssl = 'on';
-- -- ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
-- -- ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';
-- -- ALTER SYSTEM SET ssl_ca_file = '/etc/ssl/certs/ca.crt';
-- -- ALTER SYSTEM SET password_encryption = 'scram-sha-256';

-- Configure statement timeout to prevent long-running queries
-- -- ALTER SYSTEM SET statement_timeout = '30s';
-- -- ALTER SYSTEM SET lock_timeout = '10s';
-- -- ALTER SYSTEM SET idle_in_transaction_session_timeout = '5min';
-- ALTER SYSTEM SET idle_in_transaction_session_timeout = '5min';

-- Configure row security settings
-- ALTER SYSTEM SET row_security = 'on';

-- Configure audit logging
-- ALTER SYSTEM SET pgaudit.log = 'all';
-- ALTER SYSTEM SET pgaudit.log_catalog = 'off';
-- ALTER SYSTEM SET pgaudit.log_relation = 'on';
-- ALTER SYSTEM SET pgaudit.log_statement = 'all';
-- ALTER SYSTEM SET pgaudit.role = 'auditor';

-- Configure performance settings for time-series data
-- ALTER SYSTEM SET random_page_cost = 1.1;
-- ALTER SYSTEM SET effective_io_concurrency = 200;

-- Configure parallel query settings
-- ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
-- ALTER SYSTEM SET max_parallel_workers = 8;
-- ALTER SYSTEM SET parallel_tuple_cost = 0.1;
-- ALTER SYSTEM SET parallel_setup_cost = 1000.0;

-- Configure memory settings for large queries
-- ALTER SYSTEM SET hash_mem_multiplier = 1.0;
-- ALTER SYSTEM SET gin_pending_list_limit = '4MB';

-- Configure replication settings (for future scaling)
-- ALTER SYSTEM SET max_wal_senders = 3;
-- ALTER SYSTEM SET wal_keep_segments = 32;
-- ALTER SYSTEM SET archive_mode = 'on';
-- ALTER SYSTEM SET archive_command = 'cp %p /var/lib/postgresql/archive/%f';

-- Create custom configuration for VitaChain specific settings
CREATE OR REPLACE FUNCTION set_vitachain_config()
RETURNS void AS $$
BEGIN
    -- Set session-specific configurations
    SET LOCAL statement_timeout = '30s';
    SET LOCAL lock_timeout = '10s';
    SET LOCAL idle_in_transaction_session_timeout = '5min';
    
    -- Enable query plan analysis for complex queries
    SET LOCAL explain_analyze = 'on';
    SET LOCAL explain_buffers = 'on';
    SET LOCAL explain_timing = 'on';
    SET LOCAL explain_verbose = 'on';
END;
$$ LANGUAGE plpgsql;

-- Create function to monitor database performance
CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE(
    metric_name text,
    metric_value numeric,
    metric_unit text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'total_connections'::text, count(*)::numeric, 'count'::text
    FROM pg_stat_activity;
    
    RETURN QUERY
    SELECT 'active_connections'::text, count(*)::numeric, 'count'::text
    FROM pg_stat_activity 
    WHERE state = 'active';
    
    RETURN QUERY
    SELECT 'database_size'::text, pg_database_size(current_database())::numeric, 'bytes'::text;
    
    RETURN QUERY
    SELECT 'total_tables'::text, count(*)::numeric, 'count'::text
    FROM information_schema.tables 
    WHERE table_schema = 'public';
    
    RETURN QUERY
    SELECT 'total_indexes'::text, count(*)::numeric, 'count'::text
    FROM pg_indexes 
    WHERE schemaname = 'public';
    
    RETURN QUERY
    SELECT 'cache_hit_ratio'::text, 
           CASE 
               WHEN (sum(blks_hit) + sum(blks_read)) > 0 
               THEN (sum(blks_hit)::numeric / (sum(blks_hit) + sum(blks_read))) * 100 
               ELSE 0 
           END, 
           'percentage'::text
    FROM pg_stat_database 
    WHERE datname = current_database();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check database health
CREATE OR REPLACE FUNCTION check_database_health()
RETURNS TABLE(
    check_name text,
    status text,
    details text
) AS $$
BEGIN
    -- Check connection count
    RETURN QUERY
    SELECT 'connection_count'::text,
           CASE 
               WHEN count(*) < 180 THEN 'OK'
               WHEN count(*) < 195 THEN 'WARNING'
               ELSE 'CRITICAL'
           END,
           'Current connections: ' || count(*) || ' / 200 max'
    FROM pg_stat_activity;
    
    -- Check database size
    RETURN QUERY
    SELECT 'database_size'::text,
           CASE 
               WHEN pg_database_size(current_database()) < (5 * 1024 * 1024 * 1024) THEN 'OK' -- 5GB
               WHEN pg_database_size(current_database()) < (8 * 1024 * 1024 * 1024) THEN 'WARNING' -- 8GB
               ELSE 'CRITICAL'
           END,
           'Database size: ' || pg_size_pretty(pg_database_size(current_database()))
    FROM pg_database;
    
    -- Check long-running queries
    RETURN QUERY
    SELECT 'long_running_queries'::text,
           CASE 
               WHEN count(*) = 0 THEN 'OK'
               WHEN count(*) < 5 THEN 'WARNING'
               ELSE 'CRITICAL'
           END,
           'Long-running queries: ' || count(*)
    FROM pg_stat_activity 
    WHERE state = 'active' 
    AND query_start < now() - interval '30 seconds'
    AND query NOT LIKE '%check_database_health%';
    
    -- Check autovacuum status
    RETURN QUERY
    SELECT 'autovacuum_status'::text,
           CASE 
               WHEN count(*) > 0 THEN 'OK'
               ELSE 'WARNING'
           END,
           'Autovacuum workers: ' || count(*)
    FROM pg_stat_activity 
    WHERE query LIKE '%autovacuum%';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to optimize table statistics
CREATE OR REPLACE FUNCTION optimize_table_statistics()
RETURNS void AS $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE 'ANALYZE ' || quote_ident(table_record.table_name);
    END LOOP;
    
    -- Update index statistics
    FOR table_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ANALYZE ' || quote_ident(table_record.tablename);
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions on monitoring functions
GRANT EXECUTE ON FUNCTION get_database_stats() TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION check_database_health() TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION optimize_table_statistics() TO service_role;

-- Create views for easy monitoring
CREATE OR REPLACE VIEW database_overview AS
SELECT 
    'connections' as metric_type,
    count(*) as current_value,
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_value,
    round((count(*)::numeric / (SELECT setting::int FROM pg_settings WHERE name = 'max_connections')::numeric) * 100, 2) as percentage
FROM pg_stat_activity;

CREATE OR REPLACE VIEW table_sizes_overview AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Grant access to monitoring views
GRANT SELECT ON database_overview TO authenticated, service_role;
GRANT SELECT ON table_sizes_overview TO authenticated, service_role;
