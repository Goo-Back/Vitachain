"""SECONDSERVE module API routes - Restaurant Surplus Management."""

from fastapi import APIRouter
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/secondserve", tags=["secondserve"])

@router.get("/")
async def secondserve_root():
    """SECONDSERVE module root endpoint"""
    return {
        "message": "SECONDSERVE API - Restaurant Surplus Management",
        "version": "1.0.0",
        "module": "secondserve",
        "endpoints": [
            "/api/secondserve/",
            "/api/secondserve/meals",
            "/api/secondserve/reservations",
            "/api/secondserve/pickup-slots"
        ]
    }

@router.get("/health")
async def secondserve_health():
    """SECONDSERVE module health check"""
    return {
        "status": "healthy",
        "module": "secondserve",
        "version": "1.0.0"
    }

@router.get("/meals")
async def get_meals():
    """Get available meals"""
    return {
        "message": "SECONDSERVE meals endpoint",
        "meals": []
    }

@router.get("/reservations")
async def get_reservations():
    """Get reservations"""
    return {
        "message": "SECONDSERVE reservations endpoint",
        "reservations": []
    }
