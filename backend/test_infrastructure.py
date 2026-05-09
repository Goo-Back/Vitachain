#!/usr/bin/env python3
"""
Test script to validate core infrastructure services implementation.
Tests logging, caching, health checks, and monitoring functionality.
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.logging import configure_logging, get_logger
from app.core.config import get_settings
from app.core.cache import cache_service, init_cache, close_cache
from app.core.health import health_checker
from app.core.middleware import SystemMetricsCollector


async def test_logging():
    """Test structured logging configuration."""
    print("🧪 Testing structured logging...")
    
    # Configure logging
    configure_logging("INFO", "json")
    logger = get_logger("test")
    
    # Test different log levels
    logger.info("test_log_info", message="This is a test info log")
    logger.warning("test_log_warning", message="This is a test warning log")
    logger.error("test_log_error", message="This is a test error log")
    
    print("✅ Logging test completed - check output above")


async def test_cache():
    """Test Redis caching functionality."""
    print("🧪 Testing Redis cache...")
    
    try:
        # Initialize cache
        await init_cache()
        
        if not cache_service._redis:
            print("⚠️  Redis not available - cache tests will be skipped")
            return
        
        # Test basic cache operations
        test_key = "test_key"
        test_value = {"message": "Hello, Redis!", "timestamp": time.time()}
        
        # Set value
        success = await cache_service.set(test_key, test_value, expire=60)
        print(f"Cache set result: {success}")
        
        # Get value
        cached_value = await cache_service.get(test_key)
        print(f"Cache get result: {cached_value}")
        
        # Check exists
        exists = await cache_service.exists(test_key)
        print(f"Cache exists result: {exists}")
        
        # Delete value
        deleted = await cache_service.delete(test_key)
        print(f"Cache delete result: {deleted}")
        
        # Verify deletion
        exists_after_delete = await cache_service.exists(test_key)
        print(f"Cache exists after delete: {exists_after_delete}")
        
        print("✅ Cache test completed")
        
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
    finally:
        await close_cache()


async def test_health_checks():
    """Test health check endpoints."""
    print("🧪 Testing health checks...")
    
    try:
        # Test database health check
        db_health = await health_checker.check_database()
        print(f"Database health: {json.dumps(db_health, indent=2)}")
        
        # Test Redis health check
        redis_health = await health_checker.check_redis()
        print(f"Redis health: {json.dumps(redis_health, indent=2)}")
        
        # Test external API health checks (if keys are configured)
        claude_health = await health_checker.check_claude_api()
        print(f"Claude API health: {json.dumps(claude_health, indent=2)}")
        
        brevo_health = await health_checker.check_brevo_api()
        print(f"Brevo API health: {json.dumps(brevo_health, indent=2)}")
        
        openweather_health = await health_checker.check_openweather_api()
        print(f"OpenWeather API health: {json.dumps(openweather_health, indent=2)}")
        
        # Test comprehensive system health
        system_health = await health_checker.get_system_health()
        print(f"System health: {json.dumps(system_health, indent=2)}")
        
        print("✅ Health checks test completed")
        
    except Exception as e:
        print(f"❌ Health checks test failed: {e}")


async def test_metrics():
    """Test system metrics collection."""
    print("🧪 Testing system metrics...")
    
    try:
        # Test metrics collector
        metrics_collector = SystemMetricsCollector(interval=5)
        
        # Collect metrics once
        await metrics_collector._collect_and_log_metrics()
        
        print("✅ Metrics test completed - check logs above")
        
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")


async def test_configuration():
    """Test configuration loading."""
    print("🧪 Testing configuration...")
    
    try:
        settings = get_settings()
        
        print(f"App name: {settings.app_name}")
        print(f"Version: {settings.version}")
        print(f"Log level: {settings.log_level}")
        print(f"Redis URL: {settings.redis_url}")
        print(f"Enable metrics: {settings.enable_metrics}")
        print(f"API response time threshold: {settings.api_response_time_threshold}ms")
        
        print("✅ Configuration test completed")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")


async def main():
    """Run all infrastructure tests."""
    print("🚀 Starting VitaChain Core Infrastructure Services Tests")
    print("=" * 60)
    
    # Test configuration first
    await test_configuration()
    print()
    
    # Test logging
    await test_logging()
    print()
    
    # Test cache
    await test_cache()
    print()
    
    # Test health checks
    await test_health_checks()
    print()
    
    # Test metrics
    await test_metrics()
    print()
    
    print("=" * 60)
    print("🏁 Infrastructure tests completed!")
    print("\nNext steps:")
    print("1. Start Redis: docker run -d -p 6379:6379 redis:7-alpine")
    print("2. Set environment variables (see .env.example)")
    print("3. Run backend: uvicorn app.api.routes.katara:app --reload")
    print("4. Test endpoints: http://localhost:8000/api/v1/health")


if __name__ == "__main__":
    asyncio.run(main())
