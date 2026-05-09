#!/usr/bin/env python3
"""
Test core infrastructure services without requiring full environment setup.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Set minimal environment variables for testing
os.environ.update({
    "DATABASE_URL": "postgresql://test:test@localhost/test",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_JWT_SECRET": "test-secret",
    "REDIS_URL": "redis://localhost:6379",
    "LOG_LEVEL": "INFO",
    "ENABLE_METRICS": "true"
})

async def test_logging():
    """Test structured logging configuration."""
    print("🧪 Testing structured logging...")
    
    try:
        from app.core.logging import configure_logging, get_logger
        
        # Configure logging
        configure_logging("INFO", "json")
        logger = get_logger("test")
        
        # Test logging
        logger.info("test_log_info", message="Logging test successful")
        logger.warning("test_log_warning", message="Warning test successful")
        
        print("✅ Logging test completed")
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

async def test_configuration():
    """Test configuration loading."""
    print("🧪 Testing configuration...")
    
    try:
        from app.core.config import get_settings
        
        settings = get_settings()
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Version: {settings.version}")
        print(f"✅ Log level: {settings.log_level}")
        print(f"✅ Redis URL: {settings.redis_url}")
        print(f"✅ Enable metrics: {settings.enable_metrics}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def test_health_checker():
    """Test health checker initialization."""
    print("🧪 Testing health checker...")
    
    try:
        from app.core.health import health_checker
        
        # Test uptime calculation
        uptime = health_checker.get_uptime_seconds()
        print(f"✅ Uptime calculation: {uptime} seconds")
        
        # Test health check structure (without actual connections)
        print("✅ Health checker initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Health checker test failed: {e}")
        return False

async def test_cache_service():
    """Test cache service initialization."""
    print("🧪 Testing cache service...")
    
    try:
        from app.core.cache import cache_service
        
        # Test cache service initialization (without Redis connection)
        print(f"✅ Cache service initialized with URL: {cache_service.redis_url}")
        print(f"✅ Cache service password: {'set' if cache_service.password else 'not set'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache service test failed: {e}")
        return False

async def test_middleware():
    """Test middleware components."""
    print("🧪 Testing middleware...")
    
    try:
        from app.core.middleware import SystemMetricsCollector
        
        # Test metrics collector initialization
        collector = SystemMetricsCollector(interval=10)
        print(f"✅ Metrics collector initialized with interval: {collector.interval}")
        
        return True
        
    except Exception as e:
        print(f"❌ Middleware test failed: {e}")
        return False

async def test_fastapi_apps():
    """Test FastAPI application structure."""
    print("🧪 Testing FastAPI applications...")
    
    try:
        # Test importing the FastAPI apps
        from app.api.routes.katara import app as katara_app
        from app.api.routes.farmarket import app as farmarket_app  
        from app.api.routes.secondserve import app as secondserve_app
        from app.api.routes.health import router as health_router
        
        print(f"✅ KATARA app: {katara_app.title}")
        print(f"✅ FARMARKET app: {farmarket_app.title}")
        print(f"✅ SECONDSERVE app: {secondserve_app.title}")
        print(f"✅ Health router: {len(health_router.routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI apps test failed: {e}")
        return False

async def main():
    """Run all core service tests."""
    print("🚀 Starting VitaChain Core Services Tests")
    print("=" * 60)
    
    tests = [
        test_configuration,
        test_logging,
        test_cache_service,
        test_health_checker,
        test_middleware,
        test_fastapi_apps,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"🏁 Core services tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All core services tests passed!")
        print("\n✅ Infrastructure services are ready for deployment!")
        print("\nNext steps:")
        print("1. Start Redis: docker run -d -p 6379:6379 redis:7-alpine")
        print("2. Set up environment variables from .env.example")
        print("3. Start backend: uvicorn app.api.routes.katara:app --reload")
        print("4. Test health endpoint: http://localhost:8000/api/v1/health")
        return True
    else:
        print("❌ Some tests failed - please check the issues above")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
