

# ========================================
# src/monitoring/health_checker.py
# ========================================
"""Health checker pour les services."""
import asyncio
from typing import Dict, Any

from src.utils.cache import cache
from src.services.vector_db.qcadrant_client import qdrant_client


class HealthChecker:
    """Vérificateur de santé des services."""

    async def check_database(self, db_session) -> Dict[str, Any]:
        """
        Vérifier la base de données.

        Args:
            db_session: Session DB

        Returns:
            Status
        """
        try:
            from sqlalchemy import text

            await db_session.execute(text("SELECT 1"))

            return {"healthy": True, "message": "Database OK"}

        except Exception as e:
            return {"healthy": False, "message": f"Database error: {e}"}

    async def check_redis(self) -> Dict[str, Any]:
        """
        Vérifier Redis.

        Returns:
            Status
        """
        try:
            await cache.set("health_check", "ok", ttl=10)
            value = await cache.get("health_check")

            if value == "ok":
                return {"healthy": True, "message": "Redis OK"}
            else:
                return {"healthy": False, "message": "Redis response invalid"}

        except Exception as e:
            return {"healthy": False, "message": f"Redis error: {e}"}

    async def check_qdrant(self) -> Dict[str, Any]:
        """
        Vérifier Qdrant.

        Returns:
            Status
        """
        try:
            info = await qdrant_client.get_collection_info()

            if info:
                return {
                    "healthy": True,
                    "message": "Qdrant OK",
                    "points_count": info.get("points_count", 0),
                }
            else:
                return {"healthy": False, "message": "Qdrant collection not found"}

        except Exception as e:
            return {"healthy": False, "message": f"Qdrant error: {e}"}

    async def check_all(self, db_session=None) -> Dict[str, Any]:
        """
        Vérifier tous les services.

        Args:
            db_session: Session DB optionnelle

        Returns:
            Status global
        """
        checks = {}

        # Database
        if db_session:
            checks["database"] = await self.check_database(db_session)

        # Redis
        checks["redis"] = await self.check_redis()

        # Qdrant
        checks["qdrant"] = await self.check_qdrant()

        # Déterminer santé globale
        all_healthy = all(check.get("healthy", False) for check in checks.values())

        return {"healthy": all_healthy, "checks": checks}


# Instance globale
health_checker = HealthChecker()
