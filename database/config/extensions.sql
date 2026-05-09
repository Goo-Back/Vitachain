-- VitaChain Database Extensions
-- This file enables necessary PostgreSQL extensions for VitaChain

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable cryptographic functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable query statistics monitoring
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Enable full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Note: PostGIS extensions are not available by default in Supabase
-- Location-based queries will use standard decimal coordinates instead

-- Enable timestamp with time zone utilities
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Enable additional indexing methods
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Note: pg_jsonschema is not available in Supabase
-- JSONB validation will be handled at application level

-- Note: pgaudit, pg_buffercache, and pg_stat_kcache are not available in Supabase
-- These would need to be enabled in a self-hosted PostgreSQL instance

-- Enable automatic vacuum tuning (if available)
-- CREATE EXTENSION IF NOT EXISTS "pgautovacuum";
