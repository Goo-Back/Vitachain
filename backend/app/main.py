"""
Main FastAPI application for VitaChain backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.database import init_database_optimizer
from app.api.routes import auth, auth_working, health, katara, farmarket, secondserve, profiles, admin, admin_blocking, devices, notifications, telemetry

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting VitaChain backend application")
    
    # Initialize database optimizer
    from app.core.database import get_supabase_client
    supabase_client = get_supabase_client()
    await init_database_optimizer(supabase_client)
    
    # Start analysis scheduler for automatic AI analysis
    from app.services.analysis_scheduler import start_analysis_scheduler, stop_analysis_scheduler
    try:
        await start_analysis_scheduler()
        logger.info("Analysis scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start analysis scheduler: {str(e)}")
        # Continue without scheduler - automatic analysis won't work
    
    yield
    
    # Shutdown
    logger.info("Shutting down VitaChain backend application")
    try:
        await stop_analysis_scheduler()
        logger.info("Analysis scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop analysis scheduler: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="VitaChain Backend API",
    description="Backend API for VitaChain - Moroccan Agri-Food Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",  # Development
        "http://127.0.0.1:3000",  # Development
        "http://localhost:3001",  # Development
        "http://127.0.0.1:3001",  # Development
        "http://localhost:3002",  # Development
        "http://127.0.0.1:3002",  # Development
        "http://localhost:3003",  # Development
        "http://127.0.0.1:3003",  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth_working.router, tags=["authentication"])
app.include_router(profiles.router, tags=["profiles"])

# Import and include security router
from app.api.routes import security
app.include_router(security.router, tags=["security"])

# Import and include admin dashboard router
from app.api.routes import admin_dashboard
app.include_router(admin_dashboard.router, tags=["admin-dashboard"])
app.include_router(admin.router, tags=["admin"])
app.include_router(admin_blocking.router, tags=["admin-blocking"])
app.include_router(katara.router, prefix="/api/katara", tags=["katara"])
app.include_router(farmarket.router, prefix="/api/farmarket", tags=["farmarket"])
app.include_router(secondserve.router, prefix="/api/secondserve", tags=["secondserve"])
app.include_router(devices.router, tags=["devices"])
app.include_router(notifications.router, tags=["notifications"])
app.include_router(telemetry.router, tags=["telemetry"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "VitaChain Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/info")
async def info():
    """Application information."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "module": settings.module,
        "frontend_url": settings.frontend_url
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
