"""
Advanced caching service with intelligent strategies and optimization.
Provides Redis-based caching for admin dashboard user statistics and frequently accessed data
"""

import asyncio
import json
import hashlib
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import weakref

from app.core.cache import cache_service, CACHE_TTLS
from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


# Cache key generators for admin operations
def get_user_stats_key() -> str:
    """Generate cache key for user statistics."""
    return "admin:user_stats"


def get_user_list_key(filters: Dict[str, Any]) -> str:
    """Generate cache key for user list with filters."""
    filter_str = json.dumps(sorted(filters.items()), sort_keys=True)
    filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
    return f"admin:user_list:{filter_hash}"


def get_user_details_key(user_id: str) -> str:
    """Generate cache key for user details."""
    return f"admin:user_details:{user_id}"


async def invalidate_user_cache(user_id: str) -> None:
    """Invalidate all cache entries for a user."""
    patterns = [
        f"admin:user_details:{user_id}",
        f"admin:user_list:*",
        "admin:user_stats"
    ]
    
    for pattern in patterns:
        await cache_service.clear_pattern(pattern)


class CacheStrategy(Enum):
    """Cache strategy types."""
    LAZY_LOADING = "lazy_loading"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    CACHE_ASIDE = "cache_aside"
    REFRESH_AHEAD = "refresh_ahead"


class CacheInvalidationStrategy(Enum):
    """Cache invalidation strategies."""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    TAG_BASED = "tag_based"
    MANUAL = "manual"


@dataclass
class CacheConfig:
    """Cache configuration for a specific data type."""
    key_prefix: str
    ttl: int
    strategy: CacheStrategy
    invalidation_strategy: CacheInvalidationStrategy
    tags: List[str]
    warm_up_function: Optional[Callable] = None
    refresh_ahead_ratio: float = 0.8  # Refresh when 80% of TTL expired


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    data: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_access: float = 0
    tags: List[str] = None
    etag: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_access == 0:
            self.last_access = self.timestamp
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() > (self.timestamp + self.ttl)
    
    @property
    def age_ratio(self) -> float:
        """Get age as ratio of TTL (0.0 to 1.0+)."""
        age = time.time() - self.timestamp
        return age / self.ttl if self.ttl > 0 else 1.0
    
    def access(self) -> Any:
        """Access the cache entry."""
        self.access_count += 1
        self.last_access = time.time()
        return self.data


class AdvancedCacheService:
    """Advanced caching service with intelligent strategies."""
    
    def __init__(self):
        self._configs: Dict[str, CacheConfig] = {}
        self._tag_index: Dict[str, set] = {}  # tag -> set of keys
        self._refresh_tasks: Dict[str, asyncio.Task] = {}
        self._warm_up_tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default cache configurations."""
        default_configs = {
            'user_profiles': CacheConfig(
                key_prefix="profile",
                ttl=CACHE_TTLS['user_profiles'],
                strategy=CacheStrategy.CACHE_ASIDE,
                invalidation_strategy=CacheStrategy.EVENT_BASED,
                tags=["user", "profile"]
            ),
            'product_listings': CacheConfig(
                key_prefix="listings",
                ttl=CACHE_TTLS['public_listings'],
                strategy=CacheStrategy.REFRESH_AHEAD,
                invalidation_strategy=CacheStrategy.TIME_BASED,
                tags=["product", "listing", "public"],
                refresh_ahead_ratio=0.8
            ),
            'meal_listings': CacheConfig(
                key_prefix="meals",
                ttl=CACHE_TTLS['meal_data'],
                strategy=CacheStrategy.REFRESH_AHEAD,
                invalidation_strategy=CacheStrategy.TIME_BASED,
                tags=["meal", "listing", "public"],
                refresh_ahead_ratio=0.8
            ),
            'weather_data': CacheConfig(
                key_prefix="weather",
                ttl=CACHE_TTLS['weather_data'],
                strategy=CacheStrategy.CACHE_ASIDE,
                invalidation_strategy=CacheStrategy.TIME_BASED,
                tags=["weather", "external"]
            ),
            'ai_recommendations': CacheConfig(
                key_prefix="ai",
                ttl=CACHE_TTLS['ai_recommendations'],
                strategy=CacheStrategy.WRITE_BEHIND,
                invalidation_strategy=CacheStrategy.EVENT_BASED,
                tags=["ai", "recommendation"]
            ),
            'telemetry_data': CacheConfig(
                key_prefix="telemetry",
                ttl=CACHE_TTLS['telemetry_data'],
                strategy=CacheStrategy.WRITE_THROUGH,
                invalidation_strategy=CacheStrategy.TIME_BASED,
                tags=["telemetry", "iot"]
            )
        }
        
        for name, config in default_configs.items():
            self.register_config(name, config)
    
    def register_config(self, name: str, config: CacheConfig):
        """Register a cache configuration."""
        self._configs[name] = config
        
        # Initialize tag index
        for tag in config.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
    
    async def get(self, config_name: str, key: str, fetch_function: Callable = None) -> Any:
        """Get data from cache with advanced strategies."""
        config = self._configs.get(config_name)
        if not config:
            logger.warning("cache_config_not_found", config_name=config_name)
            return await self._fallback_get(key, fetch_function)
        
        cache_key = f"{config.key_prefix}:{key}"
        
        # Try to get from cache
        cached_data = await self._get_cache_entry(cache_key)
        
        if cached_data and not cached_data.is_expired:
            # Check if refresh ahead is needed
            if (config.strategy == CacheStrategy.REFRESH_AHEAD and 
                cached_data.age_ratio >= config.refresh_ahead_ratio):
                await self._schedule_refresh_ahead(config_name, key, fetch_function)
            
            # Update access statistics
            await self._update_access_stats(cache_key, cached_data)
            return cached_data.access()
        
        # Cache miss - use strategy to handle
        return await self._handle_cache_miss(config_name, key, cache_key, fetch_function, config)
    
    async def set(self, config_name: str, key: str, data: Any, tags: List[str] = None) -> bool:
        """Set data in cache with advanced strategies."""
        config = self._configs.get(config_name)
        if not config:
            logger.warning("cache_config_not_found", config_name=config_name)
            return await cache_service.set(key, data, expire=3600)
        
        cache_key = f"{config.key_prefix}:{key}"
        entry_tags = tags or config.tags
        
        # Create cache entry
        entry = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl=config.ttl,
            tags=entry_tags,
            etag=self._generate_etag(data)
        )
        
        # Store in cache
        success = await cache_service.set(cache_key, asdict(entry), expire=config.ttl)
        
        if success:
            # Update tag index
            await self._update_tag_index(cache_key, entry_tags)
            
            # Handle write-through strategy
            if config.strategy == CacheStrategy.WRITE_THROUGH:
                await self._handle_write_through(config_name, key, data)
            
            logger.debug("cache_set_success", config_name=config_name, key=key)
        else:
            logger.warning("cache_set_failed", config_name=config_name, key=key)
        
        return success
    
    async def invalidate(self, config_name: str = None, key: str = None, tags: List[str] = None) -> int:
        """Invalidate cache entries by config, key, or tags."""
        invalidated_count = 0
        
        if config_name and key:
            # Invalidate specific key
            config = self._configs.get(config_name)
            if config:
                cache_key = f"{config.key_prefix}:{key}"
                if await cache_service.delete(cache_key):
                    invalidated_count += 1
                    await self._remove_from_tag_index(cache_key)
        
        elif tags:
            # Invalidate by tags
            for tag in tags:
                keys_to_invalidate = self._tag_index.get(tag, set()).copy()
                for cache_key in keys_to_invalidate:
                    if await cache_service.delete(cache_key):
                        invalidated_count += 1
                        await self._remove_from_tag_index(cache_key)
                self._tag_index[tag] = set()
        
        return invalidated_count
    
    async def warm_up(self, config_name: str, keys: List[str] = None) -> Dict[str, Any]:
        """Warm up cache for a configuration."""
        config = self._configs.get(config_name)
        if not config or not config.warm_up_function:
            return {"error": "No warm-up function configured"}
        
        warm_up_results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        keys_to_warm = keys or await self._get_warm_up_keys(config_name)
        
        for key in keys_to_warm:
            try:
                warm_up_results["total"] += 1
                
                # Call warm-up function
                data = await config.warm_up_function(key)
                
                # Store in cache
                success = await self.set(config_name, key, data)
                if success:
                    warm_up_results["success"] += 1
                else:
                    warm_up_results["failed"] += 1
                    
            except Exception as e:
                warm_up_results["failed"] += 1
                warm_up_results["errors"].append(f"{key}: {str(e)}")
                logger.error("cache_warm_up_failed", config_name=config_name, key=key, error=str(e))
        
        return warm_up_results
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        base_stats = await cache_service.get_stats()
        
        # Add advanced stats
        advanced_stats = {
            "configurations": len(self._configs),
            "tag_index_size": sum(len(keys) for keys in self._tag_index.values()),
            "active_refresh_tasks": len(self._refresh_tasks),
            "active_warm_up_tasks": len(self._warm_up_tasks),
            "config_details": {}
        }
        
        # Add per-config stats
        for config_name, config in self._configs.items():
            config_stats = {
                "strategy": config.strategy.value,
                "ttl": config.ttl,
                "tags": config.tags,
                "refresh_ahead_ratio": config.refresh_ahead_ratio
            }
            advanced_stats["config_details"][config_name] = config_stats
        
        return {**base_stats, **advanced_stats}
    
    async def _get_cache_entry(self, cache_key: str) -> Optional[CacheEntry]:
        """Get cache entry with metadata."""
        try:
            data = await cache_service.get(cache_key)
            if data and isinstance(data, dict):
                return CacheEntry(**data)
        except Exception as e:
            logger.warning("cache_entry_deserialization_failed", key=cache_key, error=str(e))
        return None
    
    async def _update_access_stats(self, cache_key: str, entry: CacheEntry):
        """Update access statistics for cache entry."""
        # Update the entry in cache
        await cache_service.set(cache_key, asdict(entry), expire=entry.ttl)
    
    async def _handle_cache_miss(self, config_name: str, key: str, cache_key: str, 
                               fetch_function: Callable, config: CacheConfig) -> Any:
        """Handle cache miss based on strategy."""
        if not fetch_function:
            return None
        
        try:
            # Fetch data
            data = await fetch_function()
            
            # Store based on strategy
            if config.strategy in [CacheStrategy.CACHE_ASIDE, CacheStrategy.REFRESH_AHEAD]:
                await self.set(config_name, key, data)
            elif config.strategy == CacheStrategy.LAZY_LOADING:
                # Schedule lazy loading
                asyncio.create_task(self._lazy_load(config_name, key, data))
            
            return data
            
        except Exception as e:
            logger.error("cache_miss_fetch_failed", config_name=config_name, key=key, error=str(e))
            return None
    
    async def _schedule_refresh_ahead(self, config_name: str, key: str, fetch_function: Callable):
        """Schedule refresh-ahead task."""
        if not fetch_function or config_name in self._refresh_tasks:
            return
        
        config = self._configs.get(config_name)
        if not config or config.strategy != CacheStrategy.REFRESH_AHEAD:
            return
        
        # Create refresh task
        task = asyncio.create_task(self._refresh_ahead_worker(config_name, key, fetch_function))
        self._refresh_tasks[config_name] = task
        
        # Clean up task when done
        task.add_done_callback(lambda t: self._refresh_tasks.pop(config_name, None))
    
    async def _refresh_ahead_worker(self, config_name: str, key: str, fetch_function: Callable):
        """Worker for refresh-ahead strategy."""
        try:
            # Fetch fresh data
            data = await fetch_function()
            
            # Update cache
            await self.set(config_name, key, data)
            
            logger.debug("cache_refresh_ahead_success", config_name=config_name, key=key)
            
        except Exception as e:
            logger.error("cache_refresh_ahead_failed", config_name=config_name, key=key, error=str(e))
    
    async def _lazy_load(self, config_name: str, key: str, data: Any):
        """Lazy loading worker."""
        try:
            await asyncio.sleep(0.1)  # Small delay to not block response
            await self.set(config_name, key, data)
            logger.debug("cache_lazy_load_success", config_name=config_name, key=key)
        except Exception as e:
            logger.error("cache_lazy_load_failed", config_name=config_name, key=key, error=str(e))
    
    async def _handle_write_through(self, config_name: str, key: str, data: Any):
        """Handle write-through strategy."""
        # This would write to the primary data store
        # Implementation depends on specific use case
        pass
    
    async def _update_tag_index(self, cache_key: str, tags: List[str]):
        """Update tag index for cache key."""
        async with self._lock:
            for tag in tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(cache_key)
    
    async def _remove_from_tag_index(self, cache_key: str):
        """Remove cache key from tag index."""
        async with self._lock:
            for tag, keys in self._tag_index.items():
                keys.discard(cache_key)
    
    def _generate_etag(self, data: Any) -> str:
        """Generate ETag for cache data."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return f'"{hashlib.md5(data_str.encode()).hexdigest()}"'
    
    async def _get_warm_up_keys(self, config_name: str) -> List[str]:
        """Get keys for warm-up (implementation specific)."""
        # This would depend on the specific use case
        # For now, return empty list
        return []
    
    async def _fallback_get(self, key: str, fetch_function: Callable = None) -> Any:
        """Fallback get using basic cache service."""
        if fetch_function:
            data = await fetch_function()
            await cache_service.set(key, data, expire=3600)
            return data
        return await cache_service.get(key)


# Cache decorators with advanced strategies
def advanced_cache(config_name: str, key_generator: Callable = None):
    """Advanced caching decorator with strategy support."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args + tuple(sorted(kwargs.items()))))}"
            
            # Get from advanced cache
            advanced_cache = get_advanced_cache_service()
            
            async def fetch_function():
                return await func(*args, **kwargs)
            
            return await advanced_cache.get(config_name, cache_key, fetch_function)
        
        return wrapper
    return decorator


def cache_with_tags(config_name: str, tags: List[str], key_generator: Callable = None):
    """Cache decorator with tag support."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args + tuple(sorted(kwargs.items()))))}"
            
            advanced_cache = get_advanced_cache_service()
            
            # Try to get from cache
            cached = await advanced_cache.get(config_name, cache_key)
            if cached is not None:
                return cached
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await advanced_cache.set(config_name, cache_key, result, tags=tags)
            
            return result
        
        return wrapper
    return decorator


# Cache warming utilities
class CacheWarmer:
    """Utilities for cache warming."""
    
    @staticmethod
    async def warm_user_profiles(user_ids: List[str]):
        """Warm up user profiles cache."""
        advanced_cache = get_advanced_cache_service()
        
        async def fetch_profile(user_id: str):
            # This would fetch actual user profile
            return {"user_id": user_id, "name": f"User {user_id}"}
        
        # Update config with warm-up function
        config = advanced_cache._configs.get('user_profiles')
        if config:
            config.warm_up_function = fetch_profile
        
        # Warm up cache
        return await advanced_cache.warm_up('user_profiles', user_ids)
    
    @staticmethod
    async def warm_popular_listings():
        """Warm up popular product listings."""
        advanced_cache = get_advanced_cache_service()
        
        async def fetch_listings(key: str):
            # This would fetch actual listings
            return [{"id": 1, "name": "Product 1"}]
        
        # Update config with warm-up function
        config = advanced_cache._configs.get('product_listings')
        if config:
            config.warm_up_function = fetch_listings
        
        # Warm up cache with common keys
        common_keys = ["featured", "recent", "popular"]
        return await advanced_cache.warm_up('product_listings', common_keys)


# Global advanced cache service instance
_advanced_cache_service: Optional[AdvancedCacheService] = None


def get_advanced_cache_service() -> AdvancedCacheService:
    """Get global advanced cache service instance."""
    global _advanced_cache_service
    if _advanced_cache_service is None:
        _advanced_cache_service = AdvancedCacheService()
    return _advanced_cache_service


# Background tasks for cache management
async def cache_maintenance_task():
    """Background task for cache maintenance."""
    advanced_cache = get_advanced_cache_service()
    
    while True:
        try:
            # Clean up expired entries (handled by Redis TTL)
            # Clean up completed tasks
            completed_refresh_tasks = [
                name for name, task in advanced_cache._refresh_tasks.items()
                if task.done()
            ]
            for name in completed_refresh_tasks:
                advanced_cache._refresh_tasks.pop(name, None)
            
            completed_warm_up_tasks = [
                name for name, task in advanced_cache._warm_up_tasks.items()
                if task.done()
            ]
            for name in completed_warm_up_tasks:
                advanced_cache._warm_up_tasks.pop(name, None)
            
            # Sleep for maintenance interval
            await asyncio.sleep(300)  # 5 minutes
            
        except Exception as e:
            logger.error("cache_maintenance_error", error=str(e))
            await asyncio.sleep(60)  # Wait before retrying


# Cache health check
async def cache_health_check() -> Dict[str, Any]:
    """Comprehensive cache health check."""
    advanced_cache = get_advanced_cache_service()
    stats = await advanced_cache.get_stats()
    
    health_status = "healthy"
    issues = []
    
    # Check Redis connectivity
    if not stats.get("redis_connected"):
        health_status = "unhealthy"
        issues.append("Redis not connected")
    
    # Check cache hit rate
    hit_rate = stats.get("hit_rate_percent", 0)
    if hit_rate < 70:
        health_status = "degraded"
        issues.append(f"Low cache hit rate: {hit_rate}%")
    
    # Check memory usage
    memory_info = await cache_service.get_memory_info()
    if isinstance(memory_info, dict) and "used_memory_mb" in memory_info:
        used_mb = memory_info["used_memory_mb"]
        if used_mb > 200:  # 200MB threshold
            health_status = "degraded"
            issues.append(f"High memory usage: {used_mb}MB")
    
    return {
        "status": health_status,
        "issues": issues,
        "stats": stats,
        "memory_info": memory_info,
        "timestamp": time.time()
    }
