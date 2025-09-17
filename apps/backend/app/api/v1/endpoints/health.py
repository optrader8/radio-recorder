from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from datetime import datetime
import psutil
import os

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database and Redis connectivity"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "services": {}
    }

    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        await result.fetchone()
        health_status["services"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "degraded"

    # Check Redis connectivity
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        health_status["status"] = "degraded"

    # Check storage
    try:
        storage_path = settings.STORAGE_PATH
        if os.path.exists(storage_path):
            disk_usage = psutil.disk_usage(storage_path)
            free_gb = disk_usage.free / (1024**3)

            health_status["services"]["storage"] = {
                "status": "healthy" if free_gb > 1 else "warning",
                "message": f"Storage accessible, {free_gb:.2f}GB free",
                "free_space_gb": round(free_gb, 2),
                "total_space_gb": round(disk_usage.total / (1024**3), 2),
                "used_space_gb": round(disk_usage.used / (1024**3), 2)
            }

            if free_gb < 1:
                health_status["status"] = "warning"
        else:
            health_status["services"]["storage"] = {
                "status": "unhealthy",
                "message": f"Storage path {storage_path} does not exist"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        health_status["services"]["storage"] = {
            "status": "unhealthy",
            "message": f"Storage check failed: {str(e)}"
        }
        health_status["status"] = "degraded"

    # System resources
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()

        health_status["system"] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2)
        }
    except Exception as e:
        logger.error(f"System resources check failed: {e}")

    return health_status


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe endpoint"""
    try:
        # Quick database check
        result = await db.execute(text("SELECT 1"))
        await result.fetchone()

        # Quick Redis check
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()

        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}, 503


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive"}