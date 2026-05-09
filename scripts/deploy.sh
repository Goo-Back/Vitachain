#!/bin/bash

# VitaChain Deployment Script
# Automates the deployment process with validation and rollback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="/tmp/vitachain-backup-$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/tmp/vitachain-deploy-$(date +%Y%m%d_%H%M%S).log"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Print header
echo "=========================================="
echo "VitaChain Deployment Script"
echo "=========================================="
echo "Backup Directory: $BACKUP_DIR"
echo "Log File: $LOG_FILE"
echo

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if running as root (for production deployment)
    if [[ $EUID -ne 0 ]]; then
        log_warning "Not running as root. Some operations may require sudo."
    fi
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create backup
create_backup() {
    log_info "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup current containers
    if docker-compose ps | grep -q "Up"; then
        log_info "Backing up running containers..."
        docker-compose ps > "$BACKUP_DIR/containers-status.log"
        
        # Backup volumes
        docker run --rm -v vitachain_ssl:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/ssl-backup.tar.gz -C /data . 2>/dev/null || true
        
        # Backup environment file
        if [[ -f ".env" ]]; then
            cp .env "$BACKUP_DIR/"
        fi
        
        log_success "Backup created in $BACKUP_DIR"
    else
        log_info "No running containers to backup"
    fi
}

# Validate configuration
validate_configuration() {
    log_info "Validating configuration..."
    
    # Check required files
    required_files=(
        "docker-compose.yml"
        "nginx/nginx.conf"
        "nginx/conf.d/vitachain.conf"
        "frontend/Dockerfile"
        "backend/Dockerfile"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    
    # Validate Docker Compose configuration
    if ! docker-compose config >/dev/null 2>&1; then
        log_error "Docker Compose configuration is invalid"
        docker-compose config
        exit 1
    fi
    
    # Check environment file
    if [[ ! -f ".env" ]]; then
        log_warning "No .env file found. Creating from template..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            log_warning "Please edit .env with your actual values before continuing"
            read -p "Press Enter to continue after editing .env..."
        else
            log_error "No .env.example file found"
            exit 1
        fi
    fi
    
    log_success "Configuration validation passed"
}

# Build images
build_images() {
    log_info "Building Docker images..."
    
    # Build all services
    if docker-compose build; then
        log_success "Docker images built successfully"
    else
        log_error "Docker image build failed"
        exit 1
    fi
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    # Stop existing services
    if docker-compose ps | grep -q "Up"; then
        log_info "Stopping existing services..."
        docker-compose down
    fi
    
    # Start new services
    log_info "Starting new services..."
    if docker-compose up -d; then
        log_success "Services deployed successfully"
    else
        log_error "Service deployment failed"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_health() {
    log_info "Waiting for services to be healthy..."
    
    local max_wait=300  # 5 minutes
    local wait_interval=10
    local elapsed=0
    
    while [[ $elapsed -lt $max_wait ]]; do
        local healthy=true
        
        # Check NGINX
        if ! curl -f -s http://localhost/health >/dev/null 2>&1; then
            healthy=false
        fi
        
        # Check frontend
        if ! curl -f -s http://localhost:3000/api/health >/dev/null 2>&1; then
            healthy=false
        fi
        
        # Check backends
        for port in 8000 8001 8002; do
            if ! curl -f -s http://localhost:$port/health >/dev/null 2>&1; then
                healthy=false
                break
            fi
        done
        
        if [[ "$healthy" == "true" ]]; then
            log_success "All services are healthy"
            return 0
        fi
        
        log_info "Waiting for services... (${elapsed}s/${max_wait}s)"
        sleep $wait_interval
        elapsed=$((elapsed + wait_interval))
    done
    
    log_error "Services did not become healthy within timeout"
    return 1
}

# Run validation tests
run_validation() {
    log_info "Running validation tests..."
    
    if ./scripts/validate-docker.sh; then
        log_success "Validation tests passed"
    else
        log_error "Validation tests failed"
        return 1
    fi
}

# Rollback function
rollback() {
    log_error "Deployment failed. Rolling back..."
    
    # Stop current services
    docker-compose down
    
    # Restore backup if exists
    if [[ -f "$BACKUP_DIR/.env" ]]; then
        cp "$BACKUP_DIR/.env" .env
    fi
    
    # Restore SSL certificates if backup exists
    if [[ -f "$BACKUP_DIR/ssl-backup.tar.gz" ]]; then
        docker run --rm -v vitachain_ssl:/data -v "$BACKUP_DIR":/backup alpine tar xzf /backup/ssl-backup.tar.gz -C /data . 2>/dev/null || true
    fi
    
    log_info "Rollback completed. Please check logs: $LOG_FILE"
    exit 1
}

# Cleanup old images
cleanup() {
    log_info "Cleaning up old Docker images..."
    
    # Remove unused images
    docker image prune -f >/dev/null 2>&1 || true
    
    log_success "Cleanup completed"
}

# Print deployment summary
print_summary() {
    echo
    echo "=========================================="
    echo "Deployment Summary"
    echo "=========================================="
    
    # Show service status
    echo "Service Status:"
    docker-compose ps
    
    echo
    echo "Container Health:"
    docker-compose ps --format "table {{.Name}}\t{{.Status}}"
    
    echo
    echo "Access URLs:"
    echo "  Frontend: http://localhost"
    echo "  API: http://localhost/api"
    echo "  Health: http://localhost/health"
    
    echo
    echo "Useful Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    
    echo
    echo "Backup Location: $BACKUP_DIR"
    echo "Log File: $LOG_FILE"
}

# Main deployment flow
main() {
    # Trap for cleanup on exit
    trap 'log_info "Deployment interrupted"' INT TERM
    
    # Check if deployment should continue
    if docker-compose ps | grep -q "Up"; then
        log_warning "Services are currently running"
        read -p "Do you want to continue with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Run deployment steps
    check_prerequisites
    create_backup
    validate_configuration
    build_images
    
    # Deploy with rollback on failure
    if ! deploy_services; then
        rollback
    fi
    
    # Wait for health with rollback on failure
    if ! wait_for_health; then
        rollback
    fi
    
    # Run validation
    if ! run_validation; then
        log_warning "Validation failed, but services are running"
        log_info "Check logs: docker-compose logs"
    fi
    
    # Cleanup
    cleanup
    
    # Print summary
    print_summary
    
    log_success "Deployment completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    --validate-only)
        check_prerequisites
        validate_configuration
        log_success "Validation passed"
        ;;
    --backup-only)
        check_prerequisites
        create_backup
        log_success "Backup completed"
        ;;
    --rollback)
        if [[ -z "$2" ]]; then
            log_error "Please specify backup directory: --rollback /path/to/backup"
            exit 1
        fi
        BACKUP_DIR="$2"
        rollback
        ;;
    --help)
        echo "VitaChain Deployment Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --validate-only    Only validate configuration"
        echo "  --backup-only      Only create backup"
        echo "  --rollback DIR     Rollback to specified backup directory"
        echo "  --help             Show this help message"
        echo
        echo "Default: Full deployment with validation"
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
