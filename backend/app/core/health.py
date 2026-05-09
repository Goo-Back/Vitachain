"""Health check endpoints and service monitoring."""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import asyncpg
import httpx
from app.core.config import get_settings
from app.core.cache import cache_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class HealthChecker:
    """Service health monitoring."""
    
    def __init__(self):
        self.settings = get_settings()
        self.start_time = time.time()
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        start_time = time.time()
        try:
            conn = await asyncpg.connect(
                self.settings.database_url,
                server_settings={"application_name": "health-check"}
            )
            await conn.execute("SELECT 1")
            await conn.close()
            
            response_time = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error("database_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        start_time = time.time()
        try:
            if not cache_service._redis:
                return {
                    "status": "unhealthy",
                    "error": "Redis not connected",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            await cache_service._redis.ping()
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error("redis_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_claude_api(self) -> Dict[str, Any]:
        """Check Claude API availability."""
        if not self.settings.anthropic_api_key:
            return {
                "status": "not_configured",
                "error": "ANTHROPIC_API_KEY not set",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.settings.anthropic_api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "test"}]
                    }
                )
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                if response.status_code in [200, 400, 401]:  # 400/401 expected with test payload
                    return {
                        "status": "healthy",
                        "response_time_ms": response_time,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "response_time_ms": response_time,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
        except Exception as e:
            logger.error("claude_api_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_brevo_api(self) -> Dict[str, Any]:
        """Check Brevo API availability."""
        if not self.settings.brevo_api_key:
            return {
                "status": "not_configured",
                "error": "BREVO_API_KEY not set",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.brevo.com/v3/account",
                    headers={"api-key": self.settings.brevo_api_key}
                )
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "response_time_ms": response_time,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "response_time_ms": response_time,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
        except Exception as e:
            logger.error("brevo_api_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_openweather_api(self) -> Dict[str, Any]:
        """Check OpenWeather API availability."""
        if not self.settings.openweather_api_key:
            return {
                "status": "not_configured",
                "error": "OPENWEATHER_API_KEY not set",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "lat": 33.5731,  # Casablanca
                        "lon": -7.5898,
                        "appid": self.settings.openweather_api_key,
                        "units": "metric"
                    }
                )
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "response_time_ms": response_time,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "response_time_ms": response_time,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
        except Exception as e:
            logger.error("openweather_api_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_uptime_seconds(self) -> int:
        """Get application uptime in seconds."""
        return int(time.time() - self.start_time)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        # Run all health checks concurrently
        checks = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_claude_api(),
            self.check_brevo_api(),
            self.check_openweather_api(),
            return_exceptions=True
        )
        
        # Map results to service names
        services = {
            "database": checks[0] if not isinstance(checks[0], Exception) else {"status": "error", "error": str(checks[0])},
            "redis": checks[1] if not isinstance(checks[1], Exception) else {"status": "error", "error": str(checks[1])},
            "claude_api": checks[2] if not isinstance(checks[2], Exception) else {"status": "error", "error": str(checks[2])},
            "brevo_api": checks[3] if not isinstance(checks[3], Exception) else {"status": "error", "error": str(checks[3])},
            "openweather_api": checks[4] if not isinstance(checks[4], Exception) else {"status": "error", "error": str(checks[4])},
        }
        
        # Determine overall status
        unhealthy_services = [name for name, status in services.items() if status.get("status") == "unhealthy"]
        error_services = [name for name, status in services.items() if status.get("status") == "error"]
        
        overall_status = "healthy"
        if unhealthy_services or error_services:
            overall_status = "degraded" if not unhealthy_services else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": f"{self.settings.app_name} ({self.settings.module})",
            "version": self.settings.version,
            "uptime_seconds": self.get_uptime_seconds(),
            "services": services,
            "unhealthy_services": unhealthy_services + error_services
        }


# Global health checker instance
health_checker = HealthChecker()
