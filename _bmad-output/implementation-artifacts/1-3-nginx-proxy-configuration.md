# Story: 1-3-nginx-proxy-configuration

**Epic:** 1 - Platform Foundation & Infrastructure  
**Story ID:** 1.3  
**Status:** ready-for-dev  
**Created:** 2026-05-01  
**Priority:** P0 (Critical Infrastructure)

---

## User Story

**As a** platform administrator  
**I want** NGINX configured as a reverse proxy with SSL termination and security headers  
**So that** all services are securely exposed to the internet with proper security controls and performance optimization.

---

## Acceptance Criteria (BDD Format)

```gherkin
Scenario: NGINX reverse proxy handles all incoming traffic securely
  Given NGINX is running as reverse proxy on ports 80/443
  When a request comes to https://vitachain.ma
  Then it should be proxied to frontend service on port 3000
  And response should include security headers
  And SSL should be handled by Let's Encrypt certificate

Scenario: API requests are properly routed to backend services
  Given NGINX configuration is loaded
  When a request comes to https://api.vitachain.ma/api/telemetry
  Then it should be proxied to backend-katara service on port 8000
  When a request comes to https://api.vitachain.ma/api/farmarket/
  Then it should be proxied to backend-farmarket service on port 8001
  When a request comes to https://api.vitachain.ma/api/secondserve/
  Then it should be proxied to backend-secondserve service on port 8002

Scenario: Rate limiting protects against abuse
  Given NGINX rate limiting is configured
  When more than 10 requests per second come from same IP to general API
  Then requests should be throttled with HTTP 429
  When more than 100 requests per second come from same IP to telemetry endpoint
  Then requests should be throttled with HTTP 429

Scenario: SSL certificates are automatically managed
  Given Let's Encrypt certbot is installed
  When certificate is near expiration (30 days)
  Then it should be automatically renewed
  And NGINX should be reloaded gracefully

Scenario: Security headers are properly set
  Given a response is served by NGINX
  Then it should include X-Frame-Options: DENY
  And it should include X-Content-Type-Options: nosniff
  And it should include X-XSS-Protection: "1; mode=block"
  And it should include Strict-Transport-Security: "max-age=31536000"
  And it should include Referrer-Policy: "strict-origin-when-cross-origin"
```

---

## Technical Requirements

### Core NGINX Configuration
- **Reverse Proxy Setup:** Route frontend and API requests to appropriate Docker services
- **SSL Termination:** Let's Encrypt certificates with automatic renewal
- **Security Headers:** Complete OWASP-recommended security headers
- **Rate Limiting:** Per-IP rate limiting for different endpoint types
- **CORS Configuration:** Proper cross-origin resource sharing for frontend
- **Gzip Compression:** Enable compression for text-based responses
- **Health Checks:** NGINX upstream health checks for backend services

### Domain Routing
- `vitachain.ma` → Frontend Next.js (port 3000)
- `api.vitachain.ma` → Backend services with path-based routing:
  - `/api/telemetry` → backend-katara (port 8000)
  - `/api/katara/` → backend-katara (port 8000)
  - `/api/farmarket/` → backend-farmarket (port 8001)
  - `/api/secondserve/` → backend-secondserve (port 8002)

### Security Requirements
- SSL/TLS 1.3 only (disable older protocols)
- Strong cipher suites
- HSTS with preload (future-ready)
- Rate limiting per endpoint type
- IP-based blocking for abusive patterns
- Hide NGINX version in headers

### Performance Requirements
- Gzip compression for text responses
- Static asset caching with proper headers
- Connection keep-alive optimization
- Worker process optimization for VPS

---

## Architecture Compliance

### Docker Integration
- NGINX must be part of Docker Compose setup
- Use internal Docker network for service communication
- Only NGINX exposes ports 80/443 to internet
- All other services use `expose` only (no `ports`)

### Service Discovery
- Use Docker service names for upstream configuration
- Implement health checks for backend services
- Graceful degradation when backend services are down

### SSL Management
- Use certbot with NGINX plugin
- Automatic renewal via cron job
- Certificate paths: `/etc/letsencrypt/live/vitachain.ma/`
- Chain certificates properly configured

---

## Implementation Details

### File Structure
```
nginx/
├── nginx.conf                 # Main NGINX configuration
├── conf.d/
│   ├── default.conf          # Main server block configuration
│   ├── api.conf              # API routing configuration
│   └── security.conf         # Security headers and SSL settings
├── ssl/
│   └── (certbot managed)     # SSL certificates
└── Dockerfile                # NGINX container configuration
```

### Critical Configuration Sections

#### Main nginx.conf
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=telemetry:10m rate=100r/s;
    
    # Include configurations
    include /etc/nginx/conf.d/*.conf;
}
```

#### Security Headers (security.conf)
```nginx
# SSL configuration
ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# Security headers
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Hide server version
server_tokens off;
```

### Docker Compose Integration
```yaml
nginx:
  image: nginx:alpine
  container_name: vitachain-nginx
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
    - ./nginx/ssl:/etc/letsencrypt:ro
    - /etc/letsencrypt:/etc/letsencrypt:ro
  networks:
    - vitachain_network
  depends_on:
    - frontend
    - backend-katara
    - backend-farmarket
    - backend-secondserve
  restart: unless-stopped
```

---

## Testing Requirements

### Unit Tests
- NGINX configuration syntax validation
- SSL certificate validation
- Rate limiting rule testing

### Integration Tests
- End-to-end request routing verification
- SSL handshake testing
- Security headers validation
- Rate limiting behavior verification

### Performance Tests
- Load testing with concurrent requests
- SSL performance benchmarking
- Memory usage under load

### Security Tests
- SSL/TLS configuration validation (ssltest)
- Security headers verification
- Rate limiting bypass attempts
- DDoS protection validation

---

## Previous Story Intelligence

From story 1-2-docker-containerization:
- Docker network `vitachain_network` is established
- Services use internal Docker names for communication
- Only NGINX should expose ports to internet
- Environment variables are properly managed

From story 1-1-vps-deployment-setup:
- DigitalOcean VPS is configured with Ubuntu 24.04
- Docker and Docker Compose are installed
- Firewall allows ports 80 and 443
- Domain vitachain.ma points to VPS IP

---

## File Structure Requirements

### Files to CREATE:
- `nginx/nginx.conf` - Main NGINX configuration
- `nginx/conf.d/default.conf` - Frontend routing
- `nginx/conf.d/api.conf` - API routing configuration  
- `nginx/conf.d/security.conf` - Security headers and SSL
- `nginx/Dockerfile` - NGINX container setup
- `scripts/setup-ssl.sh` - SSL certificate setup script
- `scripts/renew-ssl.sh` - SSL renewal automation

### Files to UPDATE:
- `docker-compose.yml` - Add NGINX service configuration

### Files to REFERENCE:
- Existing Docker Compose configuration for service names
- VPS setup documentation for domain configuration

---

## Environment Variables Required

```bash
# Domain configuration
DOMAIN_NAME=vitachain.ma
API_DOMAIN=api.vitachain.ma

# SSL configuration
SSL_EMAIL=admin@vitachain.ma

# Service names (from Docker Compose)
FRONTEND_SERVICE=frontend
KATARA_SERVICE=backend-katara
FARMARKET_SERVICE=backend-farmarket
SECONDSERVE_SERVICE=backend-secondserve
```

---

## Success Criteria

1. **Functional Requirements:**
   - All requests route to correct services
   - SSL certificates work and auto-renew
   - Security headers are present on all responses
   - Rate limiting prevents abuse

2. **Performance Requirements:**
   - Page load times < 2.5s for frontend
   - API response times < 200ms (excluding backend processing)
   - SSL handshake < 500ms

3. **Security Requirements:**
   - A+ rating on SSL Labs test
   - All OWASP security headers present
   - Rate limiting effective against abuse
   - No server information leaked

4. **Operational Requirements:**
   - NGINX starts automatically with Docker Compose
   - Configuration reloads without downtime
   - Logs are properly rotated and accessible
   - Health checks detect service failures

---

## Rollback Plan

If issues occur during deployment:
1. Revert to previous NGINX configuration
2. Restart NGINX container with `docker-compose restart nginx`
3. Verify basic connectivity is restored
4. Investigate logs for specific issues

---

## Tasks/Subtasks

- [x] Update story status from ready-for-dev to in-progress
- [x] Create nginx directory structure and main nginx.conf file
- [x] Create nginx/conf.d/default.conf for frontend routing
- [x] Create nginx/conf.d/api.conf for API routing configuration
- [x] Create nginx/conf.d/security.conf with security headers and SSL settings
- [x] Create nginx/Dockerfile for container setup
- [x] Update docker-compose.yml to add NGINX service configuration
- [x] Create scripts/setup-ssl.sh for SSL certificate setup
- [x] Create scripts/renew-ssl.sh for SSL renewal automation
- [x] Make scripts executable and validate NGINX configuration
- [x] Update story file with implementation details and mark as review

## Dev Agent Record

### Implementation Plan
- Updated existing nginx.conf to match story specifications exactly
- Created modular configuration files (default.conf, api.conf, security.conf)
- Implemented proper SSL certificate paths for Let's Encrypt
- Added comprehensive rate limiting for different endpoint types
- Created custom Dockerfile for NGINX with health checks
- Updated docker-compose.yml to use custom build and proper dependencies
- Created SSL management scripts for setup and renewal

### Completion Notes
✅ **NGINX Proxy Configuration Complete**

**Key Accomplishments:**
- Configured reverse proxy with SSL termination using TLS 1.3
- Implemented proper domain routing (vitachain.ma → frontend, api.vitachain.ma → backends)
- Added comprehensive security headers (X-Frame-Options, HSTS, CSP, etc.)
- Configured rate limiting (10r/s general API, 100r/s telemetry)
- Created modular configuration structure for maintainability
- Set up Let's Encrypt SSL certificate management with auto-renewal
- Added health checks and proper Docker integration

**Files Created/Modified:**
- `nginx/nginx.conf` - Updated main configuration
- `nginx/conf.d/default.conf` - Frontend routing with SSL
- `nginx/conf.d/api.conf` - API routing with rate limiting
- `nginx/conf.d/security.conf` - Security headers and SSL settings
- `nginx/Dockerfile` - Custom container with health checks
- `docker-compose.yml` - Updated NGINX service configuration
- `scripts/setup-ssl.sh` - SSL certificate setup automation
- `scripts/renew-ssl.sh` - SSL renewal automation with logging

**Acceptance Criteria Met:**
- ✅ NGINX reverse proxy handles all incoming traffic securely
- ✅ API requests properly routed to backend services
- ✅ Rate limiting protects against abuse
- ✅ SSL certificates automatically managed
- ✅ Security headers properly set

## File List

### New Files:
- `nginx/conf.d/security.conf`
- `nginx/conf.d/default.conf`
- `nginx/conf.d/api.conf`
- `nginx/Dockerfile`
- `scripts/setup-ssl.sh`
- `scripts/renew-ssl.sh`

### Modified Files:
- `nginx/nginx.conf`
- `docker-compose.yml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- **2026-05-01**: Implemented complete NGINX reverse proxy configuration with SSL termination, security headers, rate limiting, and SSL certificate management automation

## Completion Status

**Status:** review  
**Completion Note:** NGINX proxy configuration fully implemented with all acceptance criteria satisfied  
**Next Steps:** Run code-review for peer validation
