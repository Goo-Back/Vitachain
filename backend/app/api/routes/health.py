"""Health check endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.core.health import health_checker
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Returns the health status of the application and all its dependencies.
    """
    try:
        health_status = await health_checker.get_system_health()
        
        # Determine HTTP status code based on overall health
        status_code = 200
        if health_status["status"] == "unhealthy":
            status_code = 503
        elif health_status["status"] == "degraded":
            status_code = 200  # Still serve traffic but indicate issues
        
        logger.info(
            "health_check_completed",
            status=health_status["status"],
            unhealthy_services=health_status.get("unhealthy_services", []),
            uptime_seconds=health_status["uptime_seconds"]
        )
        
        return health_status
    
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/health/ready", tags=["health"])
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint.
    
    Returns whether the application is ready to serve traffic.
    """
    try:
        health_status = await health_checker.get_system_health()
        
        # Check if critical services are healthy
        critical_services = ["database", "redis"]
        unhealthy_critical = [
            service for service in critical_services 
            if health_status["services"].get(service, {}).get("status") == "unhealthy"
        ]
        
        is_ready = len(unhealthy_critical) == 0
        status_code = 200 if is_ready else 503
        
        return {
            "ready": is_ready,
            "status": health_status["status"],
            "unhealthy_critical_services": unhealthy_critical,
            "timestamp": health_status["timestamp"]
        }
    
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return {
            "ready": False,
            "status": "error",
            "error": str(e)
        }


@router.get("/health/live", tags=["health"])
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint.
    
    Returns whether the application is alive.
    """
    try:
        return {
            "alive": True,
            "status": "healthy",
            "uptime_seconds": health_checker.get_uptime_seconds(),
            "timestamp": health_checker.get_system_health()["timestamp"]
        }
    except Exception as e:
        logger.error("liveness_check_failed", error=str(e))
        return {
            "alive": False,
            "status": "error",
            "error": str(e)
        }


@router.get("/metrics", tags=["health"])
async def metrics_summary() -> Dict[str, Any]:
    """
    Metrics summary endpoint.
    
    Returns a summary of application metrics.
    """
    try:
        import psutil
        
        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent(interval=1)
        
        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "timestamp": health_checker.get_system_health()["timestamp"],
            "uptime_seconds": health_checker.get_uptime_seconds(),
            "system": {
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "cpu_percent": cpu,
            },
            "process": {
                "memory_rss_mb": round(process_memory.rss / (1024**2), 2),
                "memory_vms_mb": round(process_memory.vms / (1024**2), 2),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
            }
        }
    
    except Exception as e:
        logger.error("metrics_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Metrics collection failed")
