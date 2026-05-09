# VitaChain Docker Setup Guide

This guide covers the complete Docker containerization setup for VitaChain, including production deployment, development workflow, and troubleshooting.

## Overview

VitaChain uses Docker Compose to orchestrate 5 main services:
- **NGINX** - Reverse proxy with SSL termination
- **Frontend** - Next.js 14 application
- **Backend-KATARA** - FastAPI service for smart farming
- **Backend-FARMARKET** - FastAPI service for B2B marketplace
- **Backend-SECONDSERVE** - FastAPI service for surplus food marketplace

## Quick Start

### Production Deployment

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd VitaChain.v2
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. **SSL Certificates**
   ```bash
   # Place SSL certificates in ssl/ directory
   ssl/vitachain.ma.crt
   ssl/vitachain.ma.key
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

4. **Verify**
   ```bash
   docker-compose ps
   curl https://vitachain.ma/health
   ```

### Development Setup

1. **Start Development Environment**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
   ```

2. **Access Services**
   - Frontend: http://localhost:3000
   - KATARA API: http://localhost:8000
   - FARMARKET API: http://localhost:8001
   - SECONDSERVE API: http://localhost:8002
   - NGINX: http://localhost:8080

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_DB_URL=postgresql://...
SUPABASE_JWT_SECRET=your-jwt-secret

# External APIs
ANTHROPIC_API_KEY=sk-ant-...
BREVO_API_KEY=your-brevo-key
OPENWEATHER_API_KEY=your-openweather-key

# Application
NODE_ENV=production
APP_URL=https://vitachain.ma
```

### SSL Configuration

1. **Let's Encrypt (Recommended)**
   ```bash
   certbot certonly --standalone -d vitachain.ma -d api.vitachain.ma
   cp /etc/letsencrypt/live/vitachain.ma/fullchain.pem ssl/vitachain.ma.crt
   cp /etc/letsencrypt/live/vitachain.ma/privkey.pem ssl/vitachain.ma.key
   ```

2. **Self-Signed (Development)**
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/vitachain.ma.key \
     -out ssl/vitachain.ma.crt
   ```

## Services

### NGINX Reverse Proxy

- **Ports:** 80, 443 (production), 8080, 8443 (development)
- **Configuration:** `nginx/nginx.conf`, `nginx/conf.d/vitachain.conf`
- **Features:** SSL termination, rate limiting, security headers
- **Health Check:** `/health`

### Frontend (Next.js)

- **Base Image:** `node:18.19.0-alpine`
- **Internal Port:** 3000
- **Build:** Multi-stage (deps → build → production)
- **Health Check:** `/api/health`
- **Features:** Optimized production builds, non-root user

### Backend Services (FastAPI)

All backend services share the same Dockerfile with different entry points:

- **Base Image:** `python:3.11.7-slim`
- **Internal Ports:** 8000 (KATARA), 8001 (FARMARKET), 8002 (SECONDSERVE)
- **Build:** Multi-stage (deps → production)
- **Health Check:** `/health`
- **Features:** Non-root user, virtual environment, optimized layers

## Development Workflow

### Hot Reload

The development override enables hot reload:

```bash
# Start with hot reload
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# View logs
docker-compose logs -f frontend
docker-compose logs -f backend-katara
```

### Local Database

Optional local PostgreSQL for development:

```bash
# Start with local database
docker-compose --profile local-db up -d

# Connect to database
docker exec -it vitachain-postgres-dev psql -U vitachain -d vitachain_dev
```

### Redis Cache

Optional Redis for development caching:

```bash
# Start with Redis
docker-compose --profile redis up -d

# Connect to Redis
docker exec -it vitachain-redis-dev redis-cli
```

## Operations

### Monitoring

1. **Service Status**
   ```bash
   docker-compose ps
   docker-compose top
   ```

2. **Resource Usage**
   ```bash
   docker stats
   ```

3. **Logs**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f nginx
   ```

4. **Health Checks**
   ```bash
   curl https://vitachain.ma/health
   curl https://api.vitachain.ma/health
   ```

### Maintenance

1. **Update Services**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

2. **Clean Up**
   ```bash
   docker-compose down
   docker system prune -f
   ```

3. **Backup**
   ```bash
   # Backup volumes
   docker run --rm -v vitachain_ssl:/data -v $(pwd):/backup alpine tar czf /backup/ssl-backup.tar.gz -C /data .
   ```

### Scaling

1. **Horizontal Scaling**
   ```bash
   # Scale specific services
   docker-compose up -d --scale backend-katara=2
   ```

2. **Resource Limits**
   Resource limits are pre-configured in `docker-compose.yml`:
   - NGINX: 0.5 CPU, 256MB RAM
   - Frontend: 1.0 CPU, 512MB RAM
   - Backends: 0.5 CPU, 256MB RAM each

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :80
   # Change ports in docker-compose.override.yml
   ```

2. **Permission Issues**
   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER logs/
   sudo chown -R $USER:$USER ssl/
   ```

3. **SSL Certificate Issues**
   ```bash
   # Verify certificate
   openssl x509 -in ssl/vitachain.ma.crt -text -noout
   # Check certificate path
   ls -la ssl/
   ```

4. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose logs service-name
   
   # Inspect container
   docker inspect vitachain-nginx
   ```

5. **Network Issues**
   ```bash
   # Check network
   docker network ls
   docker network inspect vitachain_vitachain_network
   
   # Recreate network
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

### Performance Issues

1. **High Memory Usage**
   ```bash
   # Check container memory
   docker stats --no-stream
   
   # Adjust limits in docker-compose.yml
   ```

2. **Slow Startup**
   ```bash
   # Check health check timeouts
   docker inspect vitachain-frontend | grep Health
   ```

3. **Database Connection Issues**
   ```bash
   # Test database connectivity
   docker exec -it vitachain-backend-katara curl $SUPABASE_URL/rest/v1/
   ```

## Security

### Best Practices

1. **Secrets Management**
   - Never commit `.env` files
   - Use Docker secrets in production
   - Rotate API keys regularly

2. **Network Security**
   - Only NGINX exposed externally
   - Internal network isolation
   - Rate limiting configured

3. **Container Security**
   - Non-root users
   - Minimal base images
   - Security scanning enabled

4. **SSL/TLS**
   - Let's Encrypt certificates
   - HSTS headers
   - Modern cipher suites

### Security Scanning

```bash
# Scan images for vulnerabilities
docker scan vitachain-frontend:latest
docker scan vitachain-backend-katara:latest
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates in place
- [ ] DNS records pointing to server
- [ ] Firewall configured (ports 80, 443 only)
- [ ] Backup strategy implemented
- [ ] Monitoring configured

### Deployment Steps

1. **Prepare Server**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy Application**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd VitaChain.v2
   
   # Configure environment
   cp .env.example .env
   # Edit .env with production values
   
   # Setup SSL
   # Place certificates in ssl/ directory
   
   # Deploy
   docker-compose up -d
   ```

3. **Verify Deployment**
   ```bash
   # Check services
   docker-compose ps
   
   # Test endpoints
   curl -k https://vitachain.ma/health
   curl -k https://api.vitachain.ma/health
   ```

### Backup and Recovery

1. **Automated Backups**
   ```bash
   # Create backup script
   cat > backup.sh << 'EOF'
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   docker-compose exec -T postgres pg_dump -U vitachain vitachain > backup_${DATE}.sql
   docker run --rm -v vitachain_ssl:/data -v $(pwd):/backup alpine tar czf /backup/ssl_${DATE}.tar.gz -C /data .
   EOF
   
   # Add to crontab
   0 2 * * * /path/to/backup.sh
   ```

2. **Recovery**
   ```bash
   # Restore database
   docker-compose exec -T postgres psql -U vitachain -d vitachain < backup_20260501_020000.sql
   
   # Restore SSL certificates
   docker run --rm -v vitachain_ssl:/data -v $(pwd):/backup alpine tar xzf /backup/ssl_20260501_020000.tar.gz -C /data
   ```

## Support

For issues and questions:
1. Check this documentation
2. Review service logs
3. Consult troubleshooting section
4. Check GitHub issues

---

**Last Updated:** 2026-05-01  
**Version:** 1.0
