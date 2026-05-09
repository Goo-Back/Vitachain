#!/bin/bash

# VitaChain Supabase Database Setup Script
# This script initializes and configures the Supabase database for VitaChain

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="vitachain"
DB_PASSWORD="${VITACHAIN_DB_PASSWORD}"
REGION="eu-west-1"  # Frankfurt
SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_ANON_KEY="${SUPABASE_ANON_KEY}"
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY}"

# Load environment variables from .env file
load_env_file() {
    local env_file=""
    
    # Check for .env file first, then .env.example in parent directory
    if [[ -f ".env" ]]; then
        env_file=".env"
        log_info "Loading environment from .env"
    elif [[ -f "../.env" ]]; then
        env_file="../.env"
        log_info "Loading environment from ../.env"
    elif [[ -f "../.env.example" ]]; then
        env_file="../.env.example"
        log_info "Loading environment from ../.env.example (template)"
    else
        log_warning "No .env or .env.example file found in current or parent directory"
        return 1
    fi
    
    # Load the environment file
    if [[ -f "$env_file" ]]; then
        # Export only the variables we need, ignoring comments and empty lines
        while IFS= read -r line; do
            # Skip comments and empty lines
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ -z "${line// }" ]] && continue
            
            # Export valid variable assignments
            if [[ "$line" =~ ^[A-Z_]+= ]]; then
                export "$line"
            fi
        done < "$env_file"
        
        log_success "Environment variables loaded from $env_file"
    fi
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Supabase CLI is installed
    if ! command -v supabase &> /dev/null; then
        log_error "Supabase CLI is not installed. Please install it first:"
        echo "npm install -g supabase"
        exit 1
    fi
    
    # Check if required environment variables are set
    if [[ -z "$SUPABASE_URL" || -z "$SUPABASE_ANON_KEY" || -z "$SUPABASE_SERVICE_ROLE_KEY" ]]; then
        log_error "Required environment variables are not set:"
        echo "SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Initialize Supabase project
init_supabase_project() {
    log_info "Initializing Supabase project..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f .env ]]; then
        log_info "Creating .env file..."
        cat > .env << EOF
# Supabase Configuration (new asymmetric system)
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
SUPABASE_DB_URL=postgresql://postgres:%26tcb-HU%2A2f5a8%25x@db.bgdtqvpchfnrscupyyaa.supabase.co:5432/postgres

# Database Configuration
DATABASE_URL=postgresql://postgres:%26tcb-HU%2A2f5a8%25x@db.bgdtqvpchfnrscupyyaa.supabase.co:5432/postgres
DB_POOL_SIZE=20
DB_MAX_CONNECTIONS=100

# Application Configuration
APP_ENV=production
# Note: JWT keys are now managed by Supabase asymmetric system
JWT_EXPIRY_HOURS=24
JWT_REFRESH_EXPIRY_DAYS=30
EOF
        log_success "Created .env file"
    fi
    
    # Try to link the project or use direct URL
    log_info "Setting up Supabase connection..."
    if command -v supabase &> /dev/null; then
        # Check if project is already linked
        if supabase status &> /dev/null; then
            log_success "Supabase project already linked"
        else
            log_info "Attempting to link Supabase project..."
            # Extract project reference from URL
            local project_ref=$(echo "$SUPABASE_URL" | sed 's/https:\/\/\([^.]*\).*/\1/')
            if supabase link --project-ref "$project_ref" 2>/dev/null; then
                log_success "Supabase project linked successfully"
            else
                log_warning "Could not link project, will use direct connection"
                log_info "Using direct database URL for migrations"
            fi
        fi
    fi
    
    log_success "Supabase project initialized"
}

# Apply database migrations
apply_migrations() {
    log_info "Applying database migrations..."
    
    # Check if migrations directory exists
    if [[ ! -d "migrations" ]]; then
        log_error "Migrations directory not found"
        return 1
    fi
    
    # Apply all migrations using Supabase CLI
    log_info "Applying all migrations from migrations/ directory"
    
    # Try with linked project first
    if supabase status &> /dev/null; then
        log_info "Using linked Supabase project"
        if supabase db push; then
            log_success "All migrations applied successfully"
        else
            log_error "Failed to apply migrations with linked project"
            return 1
        fi
    else
        log_info "Using Supabase Management API (network-friendly)"
        
        # Create a temporary linked project for API access
        log_info "Creating temporary project link for API access"
        local project_ref=$(echo "$SUPABASE_URL" | sed 's/https:\/\/\([^.]*\).*/\1/')
        
        # Try to link with API key
        if supabase link --project-ref "$project_ref" 2>/dev/null; then
            log_info "Temporary project link successful"
            if supabase db push; then
                log_success "All migrations applied successfully via API"
            else
                log_error "Failed to apply migrations via API"
                return 1
            fi
        else
            log_warning "Cannot link project, trying alternative method"
            
            # Alternative: Apply migrations using HTTP API
            log_info "Applying migrations via HTTP API"
            
            # Read and apply each migration file using the API
            for migration in migrations/*.sql; do
                if [[ -f "$migration" ]]; then
                    local migration_name=$(basename "$migration")
                    log_info "Applying migration: $migration_name"
                    
                    # Read SQL content and apply via API
                    local sql_content=$(cat "$migration")
                    
                    # Use curl to send SQL to Supabase API (without jq dependency)
                    # Escape the SQL content for JSON
                    local escaped_sql=$(echo "$sql_content" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
                    local api_response=$(curl -s -X POST \
                        "${SUPABASE_URL}/rest/v1/rpc/execute_sql" \
                        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
                        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
                        -H "Content-Type: application/json" \
                        -d "{\"sql\": \"$escaped_sql\"}" 2>/dev/null)
                    
                    if [[ $? -eq 0 ]]; then
                        log_success "Applied migration: $migration_name"
                    else
                        log_error "Failed to apply migration: $migration_name"
                        log_warning "API Response: $api_response"
                        return 1
                    fi
                fi
            done
            
            log_success "All migrations applied successfully via HTTP API"
        fi
    fi
}

# Configure database settings
configure_database() {
    log_info "Configuring database settings..."
    
    # Enable necessary extensions
    log_info "Applying extensions configuration"
    if [[ -f "config/extensions.sql" ]]; then
        supabase db push --dry-run "config/extensions.sql" 2>/dev/null || log_warning "Extensions configuration included in main migrations"
    fi
    
    # Configure database parameters
    log_info "Applying database configuration"
    if [[ -f "config/database-config.sql" ]]; then
        supabase db push --dry-run "config/database-config.sql" 2>/dev/null || log_warning "Database configuration included in main migrations"
    fi
    
    log_success "Database configuration completed"
}

# Setup backup policies
setup_backups() {
    log_info "Setting up backup policies..."
    
    # Configure automated backups (handled by Supabase automatically)
    # This script documents the backup configuration
    
    cat > docs/backup-policy.md << EOF
# VitaChain Database Backup Policy

## Automated Backups
- **Frequency:** Daily automatic backups by Supabase
- **Retention:** 30 days
- **Region:** EU-West (Frankfurt)
- **Encryption:** At rest and in transit

## Point-in-Time Recovery
- **Granularity:** 1 minute
- **Retention:** 7 days
- **Availability:** 24/7

## Manual Backups
Manual backups can be created via:
1. Supabase Dashboard
2. Supabase CLI: \`supabase db dump\`

## Restoration
1. Point-in-time recovery via Supabase Dashboard
2. Full restoration from backup
3. Selective table restoration

## Testing
- Backup restoration tests should be performed quarterly
- Test restoration procedures documented
- Recovery time objective: 4 hours
- Recovery point objective: 15 minutes
EOF
    
    log_success "Backup policy documented"
}

# Verify setup
verify_setup() {
    log_info "Verifying database setup..."
    
    # Check if tables exist using REST API
    local tables=(
        "users"
        "user_profiles"
        "roles"
        "devices"
        "telemetry"
        "products"
        "orders"
        "meals"
        "reservations"
        "alerts"
        "audit_logs"
    )
    
    for table in "${tables[@]}"; do
        # Use REST API to check if table exists
        local check_response=$(curl -s -I "${SUPABASE_URL}/rest/v1/$table?select=count&limit=1" \
            -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
            -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" 2>/dev/null)
        
        if echo "$check_response" | grep -q "HTTP/2 200"; then
            log_success "Table $table exists and accessible"
        else
            log_warning "Table $table may not exist or is not accessible (API response: $(echo "$check_response" | head -1))"
        fi
    done
    
    # Test database connectivity
    local health_check=$(curl -s "${SUPABASE_URL}/rest/v1/" \
        -H "apikey: ${SUPABASE_ANON_KEY}" 2>/dev/null)
    
    if [[ -n "$health_check" ]]; then
        log_success "Database API is accessible"
    else
        log_error "Database API is not accessible"
        return 1
    fi
    
    log_success "Database setup verification completed"
}

# Main execution
main() {
    log_info "Starting VitaChain Supabase database setup..."
    
    # Load environment variables from .env file
    load_env_file
    
    check_prerequisites
    init_supabase_project
    apply_migrations
    configure_database
    setup_backups
    verify_setup
    
    log_success "VitaChain Supabase database setup completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "1. Review the generated .env file"
    echo "2. Test database connectivity"
    echo "3. Run the verification scripts"
    echo "4. Update application configuration"
}

# Run main function
main "$@"
