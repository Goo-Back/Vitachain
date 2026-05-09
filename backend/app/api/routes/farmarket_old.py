"""FARMARKET module API routes - B2B Agricultural Marketplace."""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.cache import init_cache, close_cache
from app.core.middleware import (
    PerformanceMiddleware,
    CorrelationIDMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    metrics_collector
)
from app.api.routes.health import router as health_router

# Configure logging
settings = get_settings()
configure_logging(settings.log_level, settings.log_format)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("farmarket_backend_starting", version=settings.version)
    
    # Initialize cache
    await init_cache()
    
    # Start metrics collection
    await metrics_collector.start()
    
    logger.info("farmarket_backend_started")
    
    yield
    
    # Shutdown
    logger.info("farmarket_backend_stopping")
    
    # Stop metrics collection
    await metrics_collector.stop()
    
    # Close cache
    await close_cache()
    
    logger.info("farmarket_backend_stopped")


# Create FastAPI app
app = FastAPI(
    title="VitaChain FARMARKET Backend",
    description="B2B Agricultural Marketplace Backend Service",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vitachain.ma", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Include routers
app.include_router(health_router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "service": "VitaChain FARMARKET Backend",
        "module": "farmarket",
        "version": settings.version,
        "status": "running"
    }


@app.get("/ping", tags=["root"])
async def ping():
    """Simple ping endpoint for load balancers."""
    return {"pong": True}


if __name__ == "__main__":
    import uvicorn
    
    logger.info("starting_farmarket_backend", port=8001)
    uvicorn.run(
        "app.api.routes.farmarket:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
