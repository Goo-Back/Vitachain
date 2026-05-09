"""FastAPI dependency injection with caching and performance optimization."""

from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
from contextlib import asynccontextmanager

from app.core.cache import cache_service, cache, listings_cache, profiles_cache, products_cache, meals_cache
from app.core.performance import performance_monitor, performance_context
from app.core.database import get_database_optimizer, QueryOptimizer
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Security
security = HTTPBearer(auto_error=False)


class CacheManager:
    """Manages caching for API dependencies."""
    
    @staticmethod
    async def get_cached_listings(limit: int = 50, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """Get cached product listings."""
        cache_key = f"listings:{limit}:{offset}"
        return await cache_service.get(cache_key)
    
    @staticmethod
    async def set_cached_listings(limit: int, offset: int, listings: List[Dict[str, Any]]) -> None:
        """Set cached product listings."""
        cache_key = f"listings:{limit}:{offset}"
        await cache_service.set(cache_key, listings, expire=300)  # 5 minutes
    
    @staticmethod
    async def get_cached_meals(limit: int = 50, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """Get cached meal listings."""
        cache_key = f"meals:{limit}:{offset}"
        return await cache_service.get(cache_key)
    
    @staticmethod
    async def set_cached_meals(limit: int, offset: int, meals: List[Dict[str, Any]]) -> None:
        """Set cached meal listings."""
        cache_key = f"meals:{limit}:{offset}"
        await cache_service.set(cache_key, meals, expire=300)  # 5 minutes
    
    @staticmethod
    async def get_cached_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user profile."""
        cache_key = f"profile:{user_id}"
        return await cache_service.get(cache_key)
    
    @staticmethod
    async def set_cached_user_profile(user_id: str, profile: Dict[str, Any]) -> None:
        """Set cached user profile."""
        cache_key = f"profile:{user_id}"
        await cache_service.set(cache_key, profile, expire=1800)  # 30 minutes
    
    @staticmethod
    async def invalidate_user_cache(user_id: str) -> None:
        """Invalidate all cache entries for a user."""
        patterns = [
            f"profile:{user_id}",
            f"user_listings:{user_id}*",
            f"user_reservations:{user_id}*",
            f"user_orders:{user_id}*"
        ]
        
        for pattern in patterns:
            await cache_service.clear_pattern(pattern)


class PerformanceTracker:
    """Tracks performance for API endpoints."""
    
    @staticmethod
    @asynccontextmanager
    async def track_request(request: Request, endpoint_name: str = None):
        """Context manager for tracking request performance."""
        endpoint = endpoint_name or request.url.path
        method = request.method
        
        async with performance_context(endpoint, method):
            yield
    
    @staticmethod
    async def record_cache_hit(endpoint: str, cache_type: str = "default"):
        """Record a cache hit for performance metrics."""
        # This would update the performance monitor with cache hit info
        pass
    
    @staticmethod
    async def record_cache_miss(endpoint: str, cache_type: str = "default"):
        """Record a cache miss for performance metrics."""
        # This would update the performance monitor with cache miss info
        pass


# Dependency functions
async def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    return CacheManager()


async def get_performance_tracker() -> PerformanceTracker:
    """Get performance tracker instance."""
    return PerformanceTracker()


async def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Extract user ID from JWT token."""
    if not credentials:
        return None
    
    try:
        # This would decode the JWT and extract user ID
        # For now, return placeholder
        # TODO: Implement proper JWT decoding with Supabase
        return "user_id_placeholder"
    except Exception as e:
        logger.warning("jwt_decode_failed", error=str(e))
        return None


async def get_database_optimizer_dep() -> Optional[QueryOptimizer]:
    """Get database optimizer for query optimization."""
    db_optimizer = get_database_optimizer()
    if db_optimizer:
        return QueryOptimizer()
    return None


# Caching dependencies
def cached_listings(limit: int = 50, offset: int = 0):
    """Dependency for cached listings."""
    async def get_listings(cache_mgr: CacheManager = Depends(get_cache_manager)):
        cached = await cache_mgr.get_cached_listings(limit, offset)
        if cached:
            await cache_mgr.record_cache_hit("listings")
            return cached
        
        await cache_mgr.record_cache_miss("listings")
        return None
    
    return Depends(get_listings)


def cached_meals(limit: int = 50, offset: int = 0):
    """Dependency for cached meals."""
    async def get_meals(cache_mgr: CacheManager = Depends(get_cache_manager)):
        cached = await cache_mgr.get_cached_meals(limit, offset)
        if cached:
            await cache_mgr.record_cache_hit("meals")
            return cached
        
        await cache_mgr.record_cache_miss("meals")
        return None
    
    return Depends(get_meals)


def cached_user_profile(user_id: Optional[str] = Depends(get_current_user_id)):
    """Dependency for cached user profile."""
    async def get_profile(cache_mgr: CacheManager = Depends(get_cache_manager)):
        if not user_id:
            return None
        
        cached = await cache_mgr.get_cached_user_profile(user_id)
        if cached:
            await cache_mgr.record_cache_hit("profile")
            return cached
        
        await cache_mgr.record_cache_miss("profile")
        return None
    
    return Depends(get_profile)


# Performance monitoring dependencies
async def performance_monitoring_dep(request: Request):
    """Dependency for performance monitoring."""
    tracker = PerformanceTracker()
    async with tracker.track_request(request):
        yield tracker


# Database optimization dependencies
async def db_query_optimizer():
    """Dependency for database query optimization."""
    optimizer = get_database_optimizer_dep()
    return optimizer


# Cache invalidation utilities
class CacheInvalidationManager:
    """Manages cache invalidation strategies."""
    
    @staticmethod
    async def invalidate_product_cache(product_id: str = None, farmer_id: str = None):
        """Invalidate product-related cache entries."""
        patterns = []
        
        if product_id:
            patterns.append(f"product:{product_id}*")
        
        if farmer_id:
            patterns.append(f"farmer_products:{farmer_id}*")
        
        # Always invalidate general listings cache
        patterns.append("listings:*")
        
        for pattern in patterns:
            await cache_service.clear_pattern(pattern)
    
    @staticmethod
    async def invalidate_meal_cache(meal_id: str = None, restaurant_id: str = None):
        """Invalidate meal-related cache entries."""
        patterns = []
        
        if meal_id:
            patterns.append(f"meal:{meal_id}*")
        
        if restaurant_id:
            patterns.append(f"restaurant_meals:{restaurant_id}*")
        
        # Always invalidate general meals cache
        patterns.append("meals:*")
        
        for pattern in patterns:
            await cache_service.clear_pattern(pattern)
    
    @staticmethod
    async def invalidate_user_cache_comprehensive(user_id: str):
        """Invalidate all cache entries for a user."""
        cache_mgr = CacheManager()
        await cache_mgr.invalidate_user_cache(user_id)


# Rate limiting with caching
class RateLimiter:
    """Rate limiting with Redis cache."""
    
    @staticmethod
    async def is_rate_limited(key: str, limit: int, window: int) -> bool:
        """Check if request is rate limited."""
        current = await cache_service.get(key)
        
        if current is None:
            # First request in window
            await cache_service.set(key, 1, expire=window)
            return False
        
        if current >= limit:
            return True
        
        # Increment counter
        await cache_service.set(key, current + 1, expire=window)
        return False
    
    @staticmethod
    def get_rate_limit_key(identifier: str, endpoint: str) -> str:
        """Generate rate limit key."""
        return f"rate_limit:{identifier}:{endpoint}"


# Performance optimization decorators
def optimize_response_cache(endpoint_type: str, ttl: int = 300):
    """Decorator for optimizing response caching."""
    def decorator(func):
        @cache(expire=ttl, key_prefix=f"response:{endpoint_type}:")
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def monitor_performance(endpoint_name: str = None):
    """Decorator for monitoring function performance."""
    def decorator(func):
        @monitor_performance(endpoint_name or func.__name__)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Cache warming utilities
class CacheWarmer:
    """Utilities for warming up cache."""
    
    @staticmethod
    async def warm_popular_listings():
        """Warm up cache for popular listings."""
        # This would pre-load popular listings into cache
        pass
    
    @staticmethod
    async def warm_popular_meals():
        """Warm up cache for popular meals."""
        # This would pre-load popular meals into cache
        pass
    
    @staticmethod
    async def warm_user_profiles(user_ids: List[str]):
        """Warm up cache for user profiles."""
        cache_mgr = CacheManager()
        
        for user_id in user_ids:
            # This would fetch and cache user profile
            # Implementation would depend on user service
            pass


# Background task dependencies
async def get_cache_stats():
    """Get cache statistics for monitoring."""
    try:
        return await cache_service.get_stats()
    except Exception as e:
        logger.error("cache_stats_error", error=str(e))
        return {"error": str(e)}


async def get_performance_stats():
    """Get performance statistics for monitoring."""
    try:
        return await get_performance_summary()
    except Exception as e:
        logger.error("performance_stats_error", error=str(e))
        return {"error": str(e)}


# Health check dependencies
async def cache_health_check():
    """Check cache health."""
    try:
        # Test cache connectivity
        test_key = "health_check_test"
        await cache_service.set(test_key, "test", expire=10)
        result = await cache_service.get(test_key)
        await cache_service.delete(test_key)
        
        if result == "test":
            return {"status": "healthy", "message": "Cache is responding"}
        else:
            return {"status": "unhealthy", "message": "Cache test failed"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


async def database_health_check():
    """Check database health."""
    try:
        db_optimizer = get_database_optimizer()
        if db_optimizer:
            stats = await db_optimizer.get_database_stats(minutes=5)
            return {"status": "healthy", "message": "Database is responding", "stats": stats}
        else:
            return {"status": "unknown", "message": "Database optimizer not available"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


# Combined health check
async def performance_health_check():
    """Comprehensive performance health check."""
    cache_health = await cache_health_check()
    db_health = await database_health_check()
    
    overall_status = "healthy"
    if cache_health["status"] != "healthy" or db_health["status"] != "healthy":
        overall_status = "degraded"
    
    return {
        "overall_status": overall_status,
        "cache": cache_health,
        "database": db_health,
        "timestamp": asyncio.get_event_loop().time()
    }
