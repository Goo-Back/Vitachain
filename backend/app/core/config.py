"""Application configuration settings."""

from functools import lru_cache
from typing import Optional
import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = {
        "env_file": ".env.dev",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    # Application
    app_name: str = "VitaChain Backend"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Module Configuration
    module: str = "katara"
    
    # Database
    database_url: str = "postgresql://postgres:test@localhost:5432/test_vitachain"
    supabase_url: str = "https://demo.supabase.co"
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_jwt_secret: str = "demo-jwt-secret"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    redis_password: Optional[str] = None
    
    # External APIs
    anthropic_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    brevo_api_key: Optional[str] = None
    
    # Legacy field names for backward compatibility
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    BREVO_API_KEY: Optional[str] = None
    
    # Frontend
    frontend_url: str = "https://vitachain.ma"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_interval: int = 60
    health_check_interval: int = 30
    
    # Performance Thresholds
    api_response_time_threshold: int = 500
    memory_usage_threshold: int = 80
    cpu_usage_threshold: int = 80
    disk_usage_threshold: int = 85
    
    # Cache Configuration
    weather_cache_ttl: int = 900  # 15 minutes
    satellite_cache_ttl: int = 86400  # 24 hours
    default_cache_ttl: int = 3600  # 1 hour


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance for backward compatibility
try:
    settings = get_settings()
except Exception:
    # Fallback for testing without environment variables
    settings = Settings(
        database_url="postgresql://postgres:test@localhost:5432/test_vitachain",
        supabase_url="https://test.supabase.co",
        supabase_jwt_secret="test-jwt-secret",
        frontend_url="http://localhost:3000",
        brevo_api_key="test-brevo-key",
        BREVO_API_KEY="test-brevo-key"
    )
