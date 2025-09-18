"""Health check endpoint."""

from datetime import datetime
from fastapi import APIRouter, Depends
import asyncio
import redis.asyncio as redis

from app.schemas.common import HealthCheck
from app.core.database import get_database
from app.core.config import settings
from app import __version__

router = APIRouter()


async def check_database_connection(db) -> bool:
    """Check database connectivity."""
    try:
        await db.execute("SELECT 1")
        return True
    except Exception:
        return False


async def check_redis_connection() -> bool:
    """Check Redis connectivity."""
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthCheck)
async def health_check(db = Depends(get_database)):
    """
    Health check endpoint for monitoring service status.
    
    Returns status of:
    - API service
    - Database connection
    - Redis connection
    - Application version
    """
    # Run health checks concurrently
    db_check, redis_check = await asyncio.gather(
        check_database_connection(db),
        check_redis_connection(),
        return_exceptions=True
    )
    
    # Handle exceptions from health checks
    database_healthy = db_check is True
    redis_healthy = redis_check is True
    
    # Determine overall status
    status = "healthy" if database_healthy and redis_healthy else "degraded"
    
    return HealthCheck(
        status=status,
        timestamp=datetime.utcnow(),
        database=database_healthy,
        redis=redis_healthy,
        version=__version__
    )


@router.get("/ready")
async def readiness_check(db = Depends(get_database)):
    """Kubernetes readiness probe endpoint."""
    db_healthy = await check_database_connection(db)
    
    if not db_healthy:
        return {"status": "not ready", "reason": "database connection failed"}, 503
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive", "timestamp": datetime.utcnow()}