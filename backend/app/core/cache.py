"""Redis caching service with decorator patterns."""

import json
import hashlib
import asyncio
from functools import wraps
from typing import Any, Optional, Callable, Union
import redis.asyncio as redis
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Async Redis caching service."""
    
    def __init__(self, redis_url: str, password: Optional[str] = None):
        """Initialize Redis connection."""
        self.redis_url = redis_url
        self.password = password
        self._redis: Optional[redis.Redis] = None
        self._hits = 0
        self._misses = 0
        self._lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._redis = redis.from_url(
                self.redis_url,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            await self._redis.ping()
            logger.info("redis_connected", redis_url=self.redis_url)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            self._redis = None
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis:
            return None
        
        try:
            data = await self._redis.get(key)
            async with self._lock:
                if data:
                    self._hits += 1
                    logger.debug("cache_hit", key=key, total_hits=self._hits)
                    return json.loads(data)
                else:
                    self._misses += 1
                    logger.debug("cache_miss", key=key, total_misses=self._misses)
                    return None
        except Exception as e:
            logger.warning("cache_get_failed", key=key, error=str(e))
            async with self._lock:
                self._misses += 1
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration."""
        if not self._redis:
            return False
        
        try:
            await self._redis.setex(key, expire, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning("cache_set_failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._redis:
            return False
        
        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            logger.warning("cache_delete_failed", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._redis:
            return False
        
        try:
            return bool(await self._redis.exists(key))
        except Exception as e:
            logger.warning("cache_exists_failed", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern."""
        if not self._redis:
            return 0
        
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("cache_clear_pattern_failed", pattern=pattern, error=str(e))
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "redis_connected": self._redis is not None
            }
    
    async def reset_stats(self) -> None:
        """Reset cache statistics."""
        async with self._lock:
            self._hits = 0
            self._misses = 0
            logger.info("cache_stats_reset")
    
    async def get_memory_info(self) -> Dict[str, Any]:
        """Get Redis memory information."""
        if not self._redis:
            return {"error": "Redis not connected"}
        
        try:
            info = await self._redis.info("memory")
            return {
                "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "used_memory_peak_mb": round(info.get("used_memory_peak", 0) / 1024 / 1024, 2),
                "used_memory_rss_mb": round(info.get("used_memory_rss", 0) / 1024 / 1024, 2),
                "maxmemory_mb": round(info.get("maxmemory", 0) / 1024 / 1024, 2) if info.get("maxmemory") > 0 else None,
                "maxmemory_policy": info.get("maxmemory_policy", "unknown")
            }
        except Exception as e:
            logger.warning("cache_memory_info_failed", error=str(e))
            return {"error": str(e)}


# Global cache service instance
cache_service = CacheService(
    redis_url=get_settings().redis_url,
    password=get_settings().redis_password
)


def cache(expire: Optional[int] = None, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not cache_service._redis:
                # Cache not available, execute function directly
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug("cache_hit", key=cache_key, function=func.__name__)
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_expire = expire or get_settings().default_cache_ttl
            await cache_service.set(cache_key, result, cache_expire)
            
            logger.debug("cache_miss", key=cache_key, function=func.__name__, ttl=cache_expire)
            return result
        
        return wrapper
    return decorator


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: str) -> str:
    """Generate cache key from function and arguments."""
    # Create a string representation of arguments
    args_str = str(args + tuple(sorted(kwargs.items())))
    
    # Generate hash
    hash_input = f"{func.__module__}.{func.__name__}:{args_str}"
    hash_hex = hashlib.md5(hash_input.encode()).hexdigest()
    
    # Combine with prefix
    return f"{prefix}{func.__name__}:{hash_hex}" if prefix else f"{func.__name__}:{hash_hex}"


# Performance-specific cache TTL configurations (from story requirements)
CACHE_TTLS = {
    'weather_data': 900,      # 15 minutes
    'ai_recommendations': 3600, # 1 hour
    'public_listings': 300,    # 5 minutes
    'user_sessions': 86400,    # 24 hours
    'telemetry_data': 60,      # 1 minute
    'satellite_imagery': 86400, # 24 hours
    'api_responses': 300,       # 5 minutes
    'user_profiles': 1800,     # 30 minutes
    'product_data': 600,       # 10 minutes
    'meal_data': 300,          # 5 minutes
}

# Predefined cache decorators for common use cases
weather_cache = cache(expire=CACHE_TTLS['weather_data'], key_prefix="weather:")
satellite_cache = cache(expire=CACHE_TTLS['satellite_imagery'], key_prefix="satellite:")
ai_cache = cache(expire=CACHE_TTLS['ai_recommendations'], key_prefix="ai:")
listings_cache = cache(expire=CACHE_TTLS['public_listings'], key_prefix="listings:")
telemetry_cache = cache(expire=CACHE_TTLS['telemetry_data'], key_prefix="telemetry:")
sessions_cache = cache(expire=CACHE_TTLS['user_sessions'], key_prefix="session:")
api_cache = cache(expire=CACHE_TTLS['api_responses'], key_prefix="api:")
profiles_cache = cache(expire=CACHE_TTLS['user_profiles'], key_prefix="profile:")
products_cache = cache(expire=CACHE_TTLS['product_data'], key_prefix="product:")
meals_cache = cache(expire=CACHE_TTLS['meal_data'], key_prefix="meal:")


async def init_cache() -> None:
    """Initialize cache service connection."""
    await cache_service.connect()


async def close_cache() -> None:
    """Close cache service connection."""
    await cache_service.disconnect()
