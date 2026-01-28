"""Routes de health check et monitoring."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import get_db
from src.utils.cache import cache
from src.agent.call_manager import call_manager
from src.agent.session import session_manager

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    """Health check basique."""
    return {
        "status": "healthy",
        "service": "heyi-api",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check (database + redis)."""

    checks = {
        "database": False,
        "redis": False,
    }

    # Check database
    try:
        await db.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        print(f"❌ Database check failed: {e}")

    # Check Redis
    try:
        await cache.set("health_check", "ok", ttl=10)
        value = await cache.get("health_check")
        checks["redis"] = (value == "ok")
    except Exception as e:
        print(f"❌ Redis check failed: {e}")

    all_healthy = all(checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }


@router.get("/metrics")
async def metrics():
    """Métriques de l'application."""

    return {
        "active_calls": call_manager.get_active_calls_count(),
        "active_sessions": session_manager.get_active_sessions_count(),
        "max_concurrent_calls": call_manager.max_concurrent_calls,
    }