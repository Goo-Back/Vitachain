# Story: 1-5-core-infrastructure-services
**Epic:** 1 - Platform Foundation & Infrastructure  
**Story ID:** 1.5  
**Status:** ready-for-dev  
**Created:** 2026-05-02  
**Last Updated:** 2026-05-02  

---

## User Story

**As a** DevOps engineer  
**I want to** implement core infrastructure services including logging, monitoring, caching, and health checks  
**So that** VitaChain has observable, performant, and reliable infrastructure services supporting all platform modules

---

## Acceptance Criteria (BDD Format)

### Scenario 1: Structured Logging Implementation
```gherkin
Given the Docker Compose environment is running
When I configure structured logging with structlog
Then all application logs should be in JSON format with correlation IDs
And logs should include service name, timestamp, log level, and context
And logs should be accessible via `docker logs <container>` command
And log levels should be configurable via environment variables
```

### Scenario 2: Health Check Endpoints
```gherkin
Given all backend services are running
When I access GET /health endpoint on any service
Then the response should return 200 OK status
And the response should include service health status
And the response should include database connectivity status
And the response should include external API status (Claude, Brevo)
And the response should include timestamp and uptime information
```

### Scenario 3: Redis Caching Service
```gherkin
Given Redis container is running in Docker network
When I configure caching for frequently accessed data
Then weather data should be cached for 15 minutes
And satellite imagery should be cached for 24 hours
And API responses should be cached when appropriate
And cache should support TTL expiration
And cache should be accessible from all backend services
```

### Scenario 4: Performance Monitoring
```gherkin
Given the application is running with monitoring enabled
When I process API requests
Then response times should be tracked and logged
And database query performance should be monitored
And memory usage should be tracked per container
And CPU usage should be tracked per container
And alerts should be configured for critical thresholds
```

### Scenario 5: Error Handling and Resilience
```gherkin
Given external services may fail
When Claude API times out or returns errors
Then the application should log the error gracefully
And continue operation without AI recommendations
And implement circuit breaker pattern after repeated failures
When Brevo email service fails
Then the application should log warnings and preserve data
And retry email sending with exponential backoff
```

---

## Technical Requirements

### Core Services Implementation

#### 1. Structured Logging Service
- **Framework:** Python `structlog` with JSON formatter
- **Features:** Correlation IDs, service context, log levels
- **Configuration:** Environment-based log level control
- **Output:** JSON format for log aggregation

#### 2. Health Check Service
- **Endpoint:** `/health` on all backend services
- **Checks:** Database connectivity, external API status, service health
- **Response Format:** JSON with status, timestamp, service details
- **Monitoring:** Integration with Docker health checks

#### 3. Redis Caching Service
- **Implementation:** Redis 7.x in Docker container
- **Cache Patterns:** Time-based expiration, LRU eviction
- **Integration:** Decorator-based caching for Python services
- **Monitoring:** Cache hit/miss ratios, memory usage

#### 4. Performance Monitoring
- **Metrics:** Response times, query performance, resource usage
- **Collection:** Application-level metrics with structured logging
- **Alerting:** Configurable thresholds for critical metrics
- **Dashboard:** Log-based monitoring visualization

---

## Architecture Compliance

### Docker Compose Integration
```yaml
# Add to existing docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    expose: ["6379"]
    volumes: ["redis_data:/data"]
    command: ["redis-server", "--appendonly", "yes"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend-katara:
    # ... existing config
    environment:
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on: [redis]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Service Dependencies
- **Redis:** Required by all backend services for caching
- **Health Checks:** All services must implement `/health` endpoint
- **Logging:** Centralized logging configuration across services
- **Monitoring:** Performance tracking for all API endpoints

### Security Requirements
- **Redis:** Internal network access only, no public exposure
- **Health Endpoints:** No sensitive data in health responses
- **Logging:** No secrets or passwords in log output
- **Monitoring:** Rate limiting on monitoring endpoints

---

## Implementation Details

### 1. Logging Configuration
```python
# backend/app/core/logging.py
import structlog
import logging.config

def configure_logging(log_level: str = "INFO"):
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    })
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

### 2. Health Check Implementation
```python
# backend/app/core/health.py
from datetime import datetime
from typing import Dict, Any
import asyncpg
import httpx

async def check_database(database_url: str) -> Dict[str, Any]:
    try:
        conn = await asyncpg.connect(database_url)
        await conn.execute("SELECT 1")
        await conn.close()
        return {"status": "healthy", "response_time_ms": 10}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_external_api(api_url: str, api_key: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_url}/health",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0
            )
            return {"status": "healthy" if response.status_code == 200 else "unhealthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "katara-backend",
        "version": "1.0.0",
        "uptime_seconds": get_uptime_seconds(),
        "services": {
            "database": await check_database(settings.DATABASE_URL),
            "redis": await check_redis(settings.REDIS_URL),
            "claude_api": await check_external_api(
                "https://api.anthropic.com", 
                settings.ANTHROPIC_API_KEY
            ),
            "brevo_api": await check_external_api(
                "https://api.brevo.com",
                settings.BREVO_API_KEY
            ),
        }
    }
```

### 3. Caching Implementation
```python
# backend/app/core/cache.py
import redis.asyncio as redis
from functools import wraps
import json
import hashlib
from typing import Any, Optional

class CacheService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        try:
            await self.redis.setex(key, expire, json.dumps(value))
        except Exception:
            pass  # Cache failures should not break application
    
    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
        except Exception:
            pass

def cache(expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hashlib.md5(
                str(args + tuple(kwargs.items())).encode()
            ).hexdigest()}"
            
            cached = await cache_service.get(cache_key)
            if cached is not None:
                return cached
            
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, expire)
            return result
        return wrapper
    return decorator

# Usage examples
@cache(expire=900)  # 15 minutes
async def get_weather_data(lat: float, lng: float):
    # Weather API call
    pass

@cache(expire=86400)  # 24 hours
async def get_ndvi_image(lat: float, lng: float):
    # Satellite imagery call
    pass
```

### 4. Performance Monitoring
```python
# backend/app/core/middleware.py
import time
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000  # Convert to ms
        
        logger.info(
            "api_request",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time_ms=round(process_time, 2),
            user_agent=request.headers.get("user-agent"),
        )
        
        # Add performance headers
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        return response

# Resource monitoring
async def log_system_metrics():
    import psutil
    
    memory_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=1)
    disk_usage = psutil.disk_usage('/').percent
    
    logger.info(
        "system_metrics",
        memory_usage_percent=memory_usage,
        cpu_usage_percent=cpu_usage,
        disk_usage_percent=disk_usage,
    )
```

---

## File Structure Requirements

### New Files to Create
```
backend/app/core/
├── logging.py          # Structured logging configuration
├── health.py           # Health check implementations
├── cache.py            # Redis caching service
├── middleware.py       # Performance monitoring middleware
└── monitoring.py       # System metrics collection

backend/app/services/
└── monitoring_service.py  # Background monitoring tasks
```

### Files to Modify
```
docker-compose.yml              # Add Redis service and health checks
backend/app/main.py            # Add middleware and health endpoints
backend/app/core/config.py     # Add Redis and monitoring configuration
backend/app/core/security.py   # Add monitoring security rules
```

---

## Testing Requirements

### Unit Tests
- Test logging configuration and output format
- Test health check endpoints and responses
- Test cache service operations (get, set, delete)
- Test performance middleware metrics collection

### Integration Tests
- Test Redis connectivity from backend services
- Test health check with external service failures
- Test caching with TTL expiration
- Test monitoring with real API requests

### Performance Tests
- Verify logging overhead < 5ms per request
- Verify cache hit performance < 1ms
- Verify health check response < 100ms
- Verify monitoring middleware overhead < 2ms

---

## Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=  # Optional: if Redis requires auth

# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # json or console

# Monitoring Configuration
ENABLE_METRICS=true
METRICS_INTERVAL=60  # seconds between system metric collection
HEALTH_CHECK_INTERVAL=30  # seconds

# Performance Thresholds
API_RESPONSE_TIME_THRESHOLD=500  # ms
MEMORY_USAGE_THRESHOLD=80  # percent
CPU_USAGE_THRESHOLD=80  # percent
DISK_USAGE_THRESHOLD=85  # percent
```

---

## Previous Story Intelligence

Based on previous infrastructure stories (1-1 through 1-4):
- **VPS Setup**: Ubuntu 24.04 with Docker and security hardening
- **Docker Containerization**: Multi-service architecture with internal networking
- **NGINX Proxy**: SSL termination and security headers configured
- **Supabase Database**: PostgreSQL with RLS policies and backup strategy

**Learnings Applied:**
- Use same Docker network patterns established in 1-2
- Follow security patterns from 1-3 (internal-only services)
- Integrate with Supabase monitoring from 1-4
- Maintain same environment variable patterns

---

## Success Criteria

### Functional Success
- All services implement structured logging with correlation IDs
- Health check endpoints return proper status for all dependencies
- Redis caching improves API response times by > 20%
- Performance metrics are collected and logged for all requests

### Performance Success
- Logging overhead < 5ms per request
- Health check response < 100ms
- Cache operations < 1ms
- Monitoring middleware overhead < 2ms

### Operational Success
- All logs are in structured JSON format
- Health checks work with Docker health monitoring
- Cache survives service restarts with Redis persistence
- Monitoring provides actionable insights for performance optimization

---

## Story Completion Status

**Status:** ready-for-dev  
**Completion Note:** Core infrastructure services specification complete with logging, monitoring, caching, and health check implementations ready for development

---

## Next Steps

1. Implement structured logging configuration across all backend services
2. Create Redis caching service with decorator patterns
3. Implement health check endpoints for all services
4. Add performance monitoring middleware
5. Update Docker Compose with Redis service
6. Configure environment variables and security settings
7. Test all services with monitoring enabled
8. Validate performance improvements with caching
