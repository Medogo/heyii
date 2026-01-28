"""Gestion du cache Redis."""
import json
from typing import Any
import redis.asyncio as redis

from src.core.config import settings


class CacheManager:
    """Gestionnaire de cache Redis."""

    def __init__(self):
        self.redis: redis.Redis | None = None

    async def connect(self):
        """Connexion à Redis."""
        self.redis = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """Fermer la connexion."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Any | None:
        """Récupérer une valeur."""
        if not self.redis:
            return None

        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Stocker une valeur avec TTL."""
        if not self.redis:
            return

        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def delete(self, key: str):
        """Supprimer une clé."""
        if self.redis:
            await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Vérifier si une clé existe."""
        if not self.redis:
            return False
        return await self.redis.exists(key) > 0


# Instance globale
cache = CacheManager()