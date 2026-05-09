#!/usr/bin/env python3
"""
Basic test to validate the backend application structure without external dependencies.
"""

import sys
import os
from pathlib import Path

def test_file_structure():
    """Test that all required files exist."""
    print("🧪 Testing file structure...")
    
    required_files = [
        "app/__init__.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/logging.py",
        "app/core/cache.py",
        "app/core/health.py",
        "app/core/middleware.py",
        "app/api/__init__.py",
        "app/api/routes/__init__.py",
        "app/api/routes/health.py",
        "app/api/routes/katara.py",
        "app/api/routes/farmarket.py",
        "app/api/routes/secondserve.py",
        "requirements.txt",
        "test_infrastructure.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def test_docker_compose():
    """Test that docker-compose.yml has been updated correctly."""
    print("\n🧪 Testing Docker Compose configuration...")
    
    docker_compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    
    if not docker_compose_path.exists():
        print("❌ docker-compose.yml not found")
        return False
    
    with open(docker_compose_path, 'r') as f:
        content = f.read()
    
    # Check for Redis service
    if "redis:" in content and "redis:7-alpine" in content:
        print("✅ Redis service configured")
    else:
        print("❌ Redis service not found")
        return False
    
    # Check for Redis dependencies in backend services
    redis_dependencies = content.count("depends_on:\n      - redis")
    if redis_dependencies >= 3:  # Should be in all 3 backend services
        print(f"✅ Redis dependencies configured ({redis_dependencies} services)")
    else:
        print(f"❌ Redis dependencies missing (found {redis_dependencies}, expected 3)")
        return False
    
    # Check for monitoring environment variables
    monitoring_vars = [
        "REDIS_URL=redis://redis:6379",
        "ENABLE_METRICS=true",
        "METRICS_INTERVAL=60",
        "API_RESPONSE_TIME_THRESHOLD=500",
    ]
    
    missing_vars = []
    for var in monitoring_vars:
        if var not in content:
            missing_vars.append(var)
        else:
            print(f"✅ {var}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Docker Compose configuration looks correct")
    return True

def test_env_example():
    """Test that .env.example has been updated with infrastructure variables."""
    print("\n🧪 Testing .env.example configuration...")
    
    env_example_path = Path(__file__).parent.parent / ".env.example"
    
    if not env_example_path.exists():
        print("❌ .env.example not found")
        return False
    
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    # Check for infrastructure variables
    infrastructure_vars = [
        "REDIS_URL=redis://redis:6379",
        "ENABLE_METRICS=true",
        "METRICS_INTERVAL=60",
        "API_RESPONSE_TIME_THRESHOLD=500",
        "WEATHER_CACHE_TTL=900",
        "SATELLITE_CACHE_TTL=86400",
        "DEFAULT_CACHE_TTL=3600",
    ]
    
    missing_vars = []
    for var in infrastructure_vars:
        if var not in content:
            missing_vars.append(var)
        else:
            print(f"✅ {var}")
    
    if missing_vars:
        print(f"❌ Missing infrastructure variables: {missing_vars}")
        return False
    
    print("✅ .env.example configuration looks correct")
    return True

def test_requirements():
    """Test that requirements.txt includes necessary dependencies."""
    print("\n🧪 Testing requirements.txt...")
    
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    if not requirements_path.exists():
        print("❌ requirements.txt not found")
        return False
    
    with open(requirements_path, 'r') as f:
        content = f.read()
    
    # Check for required packages
    required_packages = [
        "fastapi>=",
        "uvicorn[standard]>=",
        "structlog>=",
        "redis>=",
        "asyncpg>=",
        "httpx>=",
        "pydantic>=",
        "psutil>=",
    ]
    
    missing_packages = []
    for package in required_packages:
        if package not in content:
            missing_packages.append(package)
        else:
            print(f"✅ {package}")
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        return False
    
    print("✅ requirements.txt looks correct")
    return True

def main():
    """Run all basic structure tests."""
    print("🚀 Starting VitaChain Core Infrastructure Basic Tests")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_docker_compose,
        test_env_example,
        test_requirements,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"🏁 Basic tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All basic structure tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start Redis: docker run -d -p 6379:6379 redis:7-alpine")
        print("3. Set environment variables: cp .env.example .env")
        print("4. Run full tests: python test_infrastructure.py")
        print("5. Start backend: uvicorn app.api.routes.katara:app --reload")
        return True
    else:
        print("❌ Some tests failed - please check the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
