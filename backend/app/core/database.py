"""Database optimization and performance monitoring utilities."""

import time
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import asyncpg
from supabase import Client, create_client

from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


class MockSupabaseClient:
    """Mock Supabase client for development/testing."""
    
    def __init__(self):
        self.auth = MockAuth()
    
    def table(self, table_name):
        return MockTable(table_name)
    
    def from_(self, table_name):
        return MockTable(table_name)


class MockAuth:
    """Mock authentication client."""
    
    def __init__(self):
        self.admin = MockAdminAuth()


class MockAdminAuth:
    """Mock admin authentication."""
    
    def get_user(self, user_id):
        class MockUser:
            def __init__(self):
                self.email = "demo@example.com"
        return MockUser()


class MockTable:
    """Mock database table operations."""
    
    def __init__(self, table_name):
        self.table_name = table_name
    
    def select(self, columns="*"):
        return self
    
    def insert(self, data):
        return MockResponse([{"id": "demo-id", **data}])
    
    def update(self, data):
        return MockResponse([{"id": "demo-id", **data}])
    
    def delete(self):
        return MockResponse([])
    
    def eq(self, column, value):
        return self
    
    def or_(self, condition):
        return self
    
    def order(self, column, desc=False):
        return self
    
    def range(self, start, end):
        return self
    
    def single(self):
        return self
    
    def execute(self):
        return MockResponse([])


class MockResponse:
    """Mock database response."""
    
    def __init__(self, data=None):
        self.data = data or []
        self.error = None


@dataclass
class QueryMetrics:
    """Database query performance metrics."""
    query: str
    query_hash: str
    execution_time_ms: float
    rows_affected: int
    timestamp: float
    error: Optional[str] = None


@dataclass
class DatabaseStats:
    """Database performance statistics."""
    total_queries: int
    avg_execution_time_ms: float
    slow_queries_count: int
    error_count: int
    connection_pool_stats: Dict[str, Any]
    timestamp: float


class DatabaseOptimizer:
    """Database performance optimization and monitoring."""
    
    def __init__(self, supabase_client: Client):
        """Initialize database optimizer."""
        self.supabase = supabase_client
        self.query_metrics: List[QueryMetrics] = []
        self._slow_query_threshold = 100.0  # ms
        self._max_metrics = 10000
        
        # Recommended indexes from story requirements
        self.recommended_indexes = [
            {
                "table": "telemetry",
                "columns": ["device_id", "timestamp DESC"],
                "type": "btree",
                "description": "Telemetry data optimization for time-series queries"
            },
            {
                "table": "telemetry", 
                "columns": ["user_id", "timestamp DESC"],
                "type": "btree",
                "description": "User telemetry queries optimization"
            },
            {
                "table": "products",
                "columns": ["is_active", "created_at DESC"],
                "type": "btree",
                "description": "Active products listing optimization"
            },
            {
                "table": "meals",
                "columns": ["is_active", "pickup_start_time", "pickup_end_time"],
                "type": "btree",
                "description": "Meal availability and pickup time optimization"
            },
            {
                "table": "products",
                "columns": ["location_lat", "location_lng"],
                "type": "gist",
                "description": "Geographic search optimization"
            }
        ]
    
    async def analyze_query_performance(self, query: str, params: List = None) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN ANALYZE."""
        try:
            # This would require direct database access through Supabase
            # For now, we'll simulate with basic timing
            start_time = time.time()
            
            # Execute query with timing
            if params:
                result = self.supabase.rpc('execute_query', {'query': query, 'params': params})
            else:
                result = self.supabase.rpc('execute_query', {'query': query})
            
            execution_time = (time.time() - start_time) * 1000
            
            # Record metrics
            metric = QueryMetrics(
                query=query[:200],  # Truncate long queries
                query_hash=self._hash_query(query),
                execution_time_ms=execution_time,
                rows_affected=len(result.data) if result.data else 0,
                timestamp=time.time()
            )
            
            self._record_metric(metric)
            
            return {
                "execution_time_ms": execution_time,
                "rows_affected": metric.rows_affected,
                "is_slow": execution_time > self._slow_query_threshold,
                "query_hash": metric.query_hash
            }
            
        except Exception as e:
            logger.error("query_analysis_failed", query=query[:100], error=str(e))
            return {
                "execution_time_ms": 0,
                "rows_affected": 0,
                "is_slow": True,
                "error": str(e)
            }
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query identification."""
        import hashlib
        # Normalize query by removing extra whitespace and lowercasing
        normalized = " ".join(query.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def _record_metric(self, metric: QueryMetrics) -> None:
        """Record query metric."""
        self.query_metrics.append(metric)
        
        # Keep only recent metrics
        if len(self.query_metrics) > self._max_metrics:
            self.query_metrics = self.query_metrics[-self._max_metrics:]
        
        # Log slow queries
        if metric.execution_time_ms > self._slow_query_threshold:
            logger.warning(
                "slow_query_detected",
                query_hash=metric.query_hash,
                execution_time_ms=metric.execution_time_ms,
                threshold_ms=self._slow_query_threshold
            )
    
    async def get_database_stats(self, minutes: int = 60) -> DatabaseStats:
        """Get database performance statistics."""
        cutoff_time = time.time() - (minutes * 60)
        recent_metrics = [
            m for m in self.query_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return DatabaseStats(
                total_queries=0,
                avg_execution_time_ms=0.0,
                slow_queries_count=0,
                error_count=0,
                connection_pool_stats={},
                timestamp=time.time()
            )
        
        execution_times = [m.execution_time_ms for m in recent_metrics]
        slow_queries = [m for m in recent_metrics if m.execution_time_ms > self._slow_query_threshold]
        error_queries = [m for m in recent_metrics if m.error is not None]
        
        return DatabaseStats(
            total_queries=len(recent_metrics),
            avg_execution_time_ms=sum(execution_times) / len(execution_times),
            slow_queries_count=len(slow_queries),
            error_count=len(error_queries),
            connection_pool_stats=await self._get_connection_pool_stats(),
            timestamp=time.time()
        )
    
    async def _get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get database connection pool statistics."""
        # This would require access to the underlying connection pool
        # For Supabase, we'll return placeholder stats
        return {
            "active_connections": "N/A (managed by Supabase)",
            "idle_connections": "N/A (managed by Supabase)",
            "total_connections": "N/A (managed by Supabase)",
            "pool_size": "N/A (managed by Supabase)"
        }
    
    async def get_slow_queries(self, limit: int = 10, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get list of slow queries."""
        cutoff_time = time.time() - (minutes * 60)
        slow_queries = [
            m for m in self.query_metrics 
            if m.timestamp >= cutoff_time and m.execution_time_ms > self._slow_query_threshold
        ]
        
        # Sort by execution time (slowest first)
        slow_queries.sort(key=lambda x: x.execution_time_ms, reverse=True)
        
        return [
            {
                "query": m.query,
                "query_hash": m.query_hash,
                "execution_time_ms": m.execution_time_ms,
                "rows_affected": m.rows_affected,
                "timestamp": m.timestamp,
                "error": m.error
            }
            for m in slow_queries[:limit]
        ]
    
    async def check_index_usage(self) -> Dict[str, Any]:
        """Check index usage and recommend optimizations."""
        # This would require database admin access
        # For now, return recommended indexes from story requirements
        return {
            "recommended_indexes": self.recommended_indexes,
            "existing_indexes": await self._get_existing_indexes(),
            "missing_indexes": await self._get_missing_indexes(),
            "index_usage_stats": await self._get_index_usage_stats()
        }
    
    async def _get_existing_indexes(self) -> List[Dict[str, Any]]:
        """Get list of existing indexes."""
        try:
            # Query to get existing indexes
            result = self.supabase.rpc('get_existing_indexes')
            return result.data if result.data else []
        except Exception as e:
            logger.warning("failed_to_get_existing_indexes", error=str(e))
            return []
    
    async def _get_missing_indexes(self) -> List[Dict[str, Any]]:
        """Get list of missing recommended indexes."""
        existing = await self._get_existing_indexes()
        existing_index_names = {idx.get('name', '') for idx in existing}
        
        missing = []
        for recommended in self.recommended_indexes:
            index_name = f"idx_{recommended['table']}_{'_'.join(recommended['columns']).replace(' ', '_').replace(',', '_')}"
            if index_name not in existing_index_names:
                missing.append(recommended)
        
        return missing
    
    async def _get_index_usage_stats(self) -> Dict[str, Any]:
        """Get index usage statistics."""
        try:
            result = self.supabase.rpc('get_index_usage_stats')
            return result.data if result.data else {}
        except Exception as e:
            logger.warning("failed_to_get_index_usage_stats", error=str(e))
            return {}
    
    async def optimize_table_queries(self, table_name: str) -> Dict[str, Any]:
        """Get optimization recommendations for a specific table."""
        table_stats = await self._get_table_stats(table_name)
        slow_queries = await self._get_table_slow_queries(table_name)
        index_recommendations = await self._get_table_index_recommendations(table_name)
        
        return {
            "table_name": table_name,
            "table_stats": table_stats,
            "slow_queries": slow_queries,
            "index_recommendations": index_recommendations,
            "optimization_score": self._calculate_optimization_score(table_stats, slow_queries)
        }
    
    async def _get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics."""
        try:
            result = self.supabase.rpc('get_table_stats', {'table_name': table_name})
            return result.data if result.data else {}
        except Exception as e:
            logger.warning("failed_to_get_table_stats", table=table_name, error=str(e))
            return {}
    
    async def _get_table_slow_queries(self, table_name: str) -> List[Dict[str, Any]]:
        """Get slow queries for a specific table."""
        all_slow = await self.get_slow_queries(limit=100, minutes=60)
        return [q for q in all_slow if table_name.lower() in q['query'].lower()]
    
    async def _get_table_index_recommendations(self, table_name: str) -> List[Dict[str, Any]]:
        """Get index recommendations for a specific table."""
        table_indexes = [idx for idx in self.recommended_indexes if idx['table'] == table_name]
        missing = await self._get_missing_indexes()
        return [idx for idx in table_indexes if idx in missing]
    
    def _calculate_optimization_score(self, table_stats: Dict, slow_queries: List) -> int:
        """Calculate optimization score for a table (0-100)."""
        score = 100
        
        # Deduct points for slow queries
        if slow_queries:
            score -= min(len(slow_queries) * 10, 50)
        
        # Deduct points for large tables without proper indexing
        row_count = table_stats.get('row_count', 0)
        if row_count > 10000:  # Large table
            score -= 20
        
        return max(0, score)
    
    @asynccontextmanager
    async def query_monitor(self, query: str, params: List = None):
        """Context manager for monitoring query performance."""
        start_time = time.time()
        error = None
        rows_affected = 0
        
        try:
            yield
            # Success case - rows affected would be set by the caller
        except Exception as e:
            error = str(e)
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000
            
            # Record metric
            metric = QueryMetrics(
                query=query[:200],
                query_hash=self._hash_query(query),
                execution_time_ms=execution_time,
                rows_affected=rows_affected,
                timestamp=time.time(),
                error=error
            )
            
            self._record_metric(metric)
    
    def clear_old_metrics(self, hours: int = 24) -> None:
        """Clear metrics older than specified hours."""
        cutoff_time = time.time() - (hours * 3600)
        self.query_metrics = [m for m in self.query_metrics if m.timestamp >= cutoff_time]


# Database query optimization utilities
class QueryOptimizer:
    """Static utilities for query optimization."""
    
    @staticmethod
    def optimize_telemetry_query(device_id: str, limit: int = 100, hours: int = 24) -> Dict[str, Any]:
        """Generate optimized telemetry query."""
        # Input validation
        if not device_id or not isinstance(device_id, str):
            raise ValueError("device_id must be a non-empty string")
        if not isinstance(limit, int) or limit <= 0 or limit > 10000:
            raise ValueError("limit must be a positive integer <= 10000")
        if not isinstance(hours, int) or hours <= 0 or hours > 720:  # Max 30 days
            raise ValueError("hours must be a positive integer <= 720")
            
        return {
            "table": "telemetry",
            "columns": ["timestamp", "sensor_type", "value", "unit"],
            "where": {
                "device_id": device_id,
                "timestamp": f">= NOW() - INTERVAL '{hours} hours'"
            },
            "order_by": "timestamp DESC",
            "limit": limit,
            "index_hint": "idx_telemetry_device_time"
        }
    
    @staticmethod
    def optimize_products_query(
        is_active: bool = True,
        limit: int = 50,
        location_lat: float = None,
        location_lng: float = None,
        radius_km: float = 50
    ) -> Dict[str, Any]:
        """Generate optimized products query."""
        query = {
            "table": "products",
            "columns": ["id", "name", "price", "quantity", "location_lat", "location_lng", "created_at"],
            "where": {"is_active": is_active},
            "order_by": "created_at DESC",
            "limit": limit,
            "index_hint": "idx_products_is_active_created_at"
        }
        
        # Add geographic filter if coordinates provided
        if location_lat and location_lng:
            query["where"].update({
                "location_filter": f"ST_DWithin(POINT(location_lng, location_lat), POINT({location_lng}, {location_lat}), {radius_km})"
            })
            query["index_hint"] = "idx_products_location"
        
        return query
    
    @staticmethod
    def optimize_meals_query(
        is_active: bool = True,
        pickup_time_start: str = None,
        pickup_time_end: str = None
    ) -> Dict[str, Any]:
        """Generate optimized meals query."""
        query = {
            "table": "meals",
            "columns": ["id", "name", "discount_price", "available_quantity", "pickup_start_time", "pickup_end_time"],
            "where": {"is_active": is_active},
            "order_by": "pickup_start_time ASC",
            "index_hint": "idx_meals_active_pickup_time"
        }
        
        # Add time range filter if provided
        if pickup_time_start and pickup_time_end:
            query["where"].update({
                "pickup_time_range": f"pickup_start_time >= '{pickup_time_start}' AND pickup_end_time <= '{pickup_time_end}'"
            })
        
        return query


# Global database optimizer instance (will be initialized with Supabase client)
database_optimizer: Optional[DatabaseOptimizer] = None


def get_supabase_client(service_role: bool = False) -> Client:
    """Get Supabase client instance."""
    settings = get_settings()
    
    # Handle demo/development credentials
    if (settings.supabase_url == "https://demo.supabase.co" or 
        settings.supabase_jwt_secret == "demo-jwt-secret"):
        # Return a mock client for development
        return MockSupabaseClient()
    
    try:
        # Use service role key for bypassing RLS (required for telemetry insertion)
        if service_role:
            service_key = getattr(settings, 'supabase_service_role_key', settings.supabase_anon_key)
            if not service_key:
                raise ValueError("Service role key is required for service_role client")
            # Try creating client with explicit kwargs to avoid proxy issue
            try:
                return create_client(
                    supabase_url=settings.supabase_url,
                    supabase_key=service_key
                )
            except TypeError:
                # Fallback for different versions
                return create_client(settings.supabase_url, service_key)
        else:
            anon_key = getattr(settings, 'supabase_anon_key', None)
            if not anon_key:
                raise ValueError("Anonymous key is required for public client")
            # Try creating client with explicit kwargs to avoid proxy issue
            try:
                return create_client(
                    supabase_url=settings.supabase_url,
                    supabase_key=anon_key
                )
            except TypeError:
                # Fallback for different versions
                return create_client(settings.supabase_url, anon_key)
    except Exception as e:
        logger.warning(f"Failed to create Supabase client: {e}")
        return MockSupabaseClient()


async def init_database_optimizer(supabase_client: Client) -> DatabaseOptimizer:
    """Initialize database optimizer with Supabase client."""
    global database_optimizer
    database_optimizer = DatabaseOptimizer(supabase_client)
    logger.info("database_optimizer_initialized")
    return database_optimizer


def get_database_optimizer() -> Optional[DatabaseOptimizer]:
    """Get global database optimizer instance."""
    return database_optimizer


# Database performance monitoring task
async def database_monitoring_task() -> None:
    """Background task for database performance monitoring."""
    while True:
        try:
            if database_optimizer:
                # Collect database stats
                stats = await database_optimizer.get_database_stats(minutes=5)
                
                # Log performance warnings
                if stats.avg_execution_time_ms > 100:
                    logger.warning(
                        "high_avg_query_time",
                        avg_time_ms=stats.avg_execution_time_ms
                    )
                
                if stats.slow_queries_count > 10:
                    logger.warning(
                        "high_slow_query_count",
                        slow_queries=stats.slow_queries_count
                    )
                
                # Clean up old metrics
                database_optimizer.clear_old_metrics(hours=24)
            
            # Sleep for configured interval
            await asyncio.sleep(300)  # 5 minutes
            
        except Exception as e:
            logger.error("database_monitoring_error", error=str(e))
            await asyncio.sleep(300)  # Wait before retrying
