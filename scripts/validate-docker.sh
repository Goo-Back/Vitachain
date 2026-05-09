#!/bin/bash

# VitaChain Docker Validation Script
# Tests all Docker services and configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

run_test() {
    ((TESTS_TOTAL++))
    local test_name="$1"
    local test_command="$2"
    
    log_info "Running: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        log_success "$test_name"
        return 0
    else
        log_error "$test_name"
        return 1
    fi
}

# Print header
echo "=========================================="
echo "VitaChain Docker Validation Suite"
echo "=========================================="
echo

# Check if Docker is running
log_info "Checking Docker daemon..."
if ! docker info >/dev/null 2>&1; then
    log_error "Docker daemon is not running"
    exit 1
else
    log_success "Docker daemon is running"
fi

# Check if Docker Compose is available
log_info "Checking Docker Compose..."
if ! command -v docker-compose >/dev/null 2>&1; then
    log_error "Docker Compose is not installed"
    exit 1
else
    log_success "Docker Compose is available"
fi

# Validate Docker Compose configuration
log_info "Validating Docker Compose configuration..."
if docker-compose config >/dev/null 2>&1; then
    log_success "Docker Compose configuration is valid"
else
    log_error "Docker Compose configuration has errors"
    docker-compose config
    exit 1
fi

# Check required files
log_info "Checking required files..."
required_files=(
    "docker-compose.yml"
    ".env.example"
    "nginx/nginx.conf"
    "nginx/conf.d/vitachain.conf"
    "frontend/Dockerfile"
    "backend/Dockerfile"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        log_success "Required file exists: $file"
        ((TESTS_PASSED++))
    else
        log_error "Required file missing: $file"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
done

# Check environment file
log_info "Checking environment configuration..."
if [[ -f ".env" ]]; then
    # Check for required environment variables
    required_vars=(
        "SUPABASE_URL"
        "SUPABASE_DB_URL"
        "SUPABASE_JWT_SECRET"
        "NODE_ENV"
    )
    
    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" .env 2>/dev/null; then
            log_success "Environment variable set: $var"
            ((TESTS_PASSED++))
        else
            log_error "Environment variable missing: $var"
            ((TESTS_FAILED++))
        fi
        ((TESTS_TOTAL++))
    done
else
    log_info "No .env file found (expected for first-time setup)"
fi

# Check SSL certificates
log_info "Checking SSL certificates..."
if [[ -f "ssl/vitachain.ma.crt" ]] && [[ -f "ssl/vitachain.ma.key" ]]; then
    log_success "SSL certificate files exist"
    
    # Validate certificate format
    if openssl x509 -in ssl/vitachain.ma.crt -noout -text >/dev/null 2>&1; then
        log_success "SSL certificate is valid"
        ((TESTS_PASSED++))
    else
        log_error "SSL certificate is invalid"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
    
    # Check certificate permissions
    if [[ $(stat -c %a ssl/vitachain.ma.key) == "600" ]] || [[ $(stat -c %a ssl/vitachain.ma.key) == "640" ]]; then
        log_success "SSL key has appropriate permissions"
        ((TESTS_PASSED++))
    else
        log_error "SSL key permissions are too open"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
else
    log_info "SSL certificates not found (run setup-ssl.sh)"
fi

# Check directory structure
log_info "Checking directory structure..."
required_dirs=(
    "logs/nginx"
    "ssl"
    "backups/supabase"
    "nginx/conf.d"
)

for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        log_success "Directory exists: $dir"
        ((TESTS_PASSED++))
    else
        log_error "Directory missing: $dir"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
done

# Test Docker image builds (if containers are not running)
if ! docker-compose ps | grep -q "Up"; then
    log_info "Testing Docker image builds..."
    
    # Test frontend build
    log_info "Building frontend image..."
    if docker-compose build frontend >/dev/null 2>&1; then
        log_success "Frontend image builds successfully"
    else
        log_error "Frontend image build failed"
    fi
    ((TESTS_TOTAL++))
    
    # Test backend build
    log_info "Building backend image..."
    if docker-compose build backend-katara >/dev/null 2>&1; then
        log_success "Backend image builds successfully"
    else
        log_error "Backend image build failed"
    fi
    ((TESTS_TOTAL++))
fi

# Test service connectivity (if containers are running)
if docker-compose ps | grep -q "Up"; then
    log_info "Testing service connectivity..."
    
    # Test NGINX health
    run_test "NGINX health check" "curl -f -s http://localhost/health"
    
    # Test frontend health
    run_test "Frontend health check" "curl -f -s http://localhost:3000/api/health"
    
    # Test backend health checks
    run_test "KATARA backend health" "curl -f -s http://localhost:8000/health"
    run_test "FARMARKET backend health" "curl -f -s http://localhost:8001/health"
    run_test "SECONDSERVE backend health" "curl -f -s http://localhost:8002/health"
    
    # Test API routing through NGINX
    run_test "API routing (KATARA)" "curl -f -s http://localhost/api/katara/health"
    run_test "API routing (FARMARKET)" "curl -f -s http://localhost/api/farmarket/health"
    run_test "API routing (SECONDSERVE)" "curl -f -s http://localhost/api/secondserve/health"
    
    # Test SSL (if certificates are present)
    if [[ -f "ssl/vitachain.ma.crt" ]]; then
        run_test "HTTPS health check" "curl -f -s -k https://localhost:8443/health"
    fi
else
    log_info "Containers are not running - skipping connectivity tests"
fi

# Test Docker network
log_info "Testing Docker network..."
if docker network ls | grep -q "vitachain_vitachain_network"; then
    log_success "Docker network exists"
    
    # Test network configuration
    network_info=$(docker network inspect vitachain_vitachain_network 2>/dev/null | jq -r '.[0].IPAM.Config[0].Subnet' 2>/dev/null || echo "")
    if [[ -n "$network_info" ]]; then
        log_success "Network subnet configured: $network_info"
        ((TESTS_PASSED++))
    else
        log_error "Network subnet not configured"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
else
    log_info "Docker network not created (run docker-compose up)"
fi

# Test resource limits
log_info "Testing resource limits configuration..."
if docker-compose config | grep -q "deploy:"; then
    log_success "Resource limits are configured"
    ((TESTS_PASSED++))
else
    log_error "Resource limits not found in configuration"
    ((TESTS_FAILED++))
fi
((TESTS_TOTAL++))

# Check for security configurations
log_info "Checking security configurations..."

# Test non-root user configuration
if grep -q "user:" docker-compose.yml 2>/dev/null; then
    log_success "Non-root user configuration found"
    ((TESTS_PASSED++))
else
    log_info "Non-root user configuration not explicitly set"
fi
((TESTS_TOTAL++))

# Test health check configuration
health_check_count=$(grep -c "healthcheck:" docker-compose.yml 2>/dev/null || echo "0")
if [[ $health_check_count -gt 0 ]]; then
    log_success "Health checks configured ($health_check_count services)"
    ((TESTS_PASSED++))
else
    log_error "No health checks configured"
    ((TESTS_FAILED++))
fi
((TESTS_TOTAL++))

# Print summary
echo
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo "Total Tests: $TESTS_TOTAL"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review the output above.${NC}"
    exit 1
fi
