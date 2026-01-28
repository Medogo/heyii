
# ========================================
# src/api/middleware/rate_limit.py
# ========================================
"""Middleware de rate limiting."""
from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict


class RateLimiter:
    """Rate limiter basique."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialiser le rate limiter.

        Args:
            max_requests: Nombre max de requêtes
            window_seconds: Fenêtre temporelle (secondes)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    async def __call__(self, request: Request):
        """
        Middleware FastAPI.

        Args:
            request: Requête FastAPI

        Raises:
            HTTPException: Si limite atteinte
        """
        # Identifier le client (IP ou user)
        client_id = request.client.host

        # Nettoyer les anciennes requêtes
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)

        self.requests[client_id] = [
            req_time
            for req_time in self.requests[client_id]
            if req_time > cutoff
        ]

        # Vérifier la limite
        if len(self.requests[client_id]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit dépassé: {self.max_requests} requêtes par {self.window_seconds}s",
            )

        # Ajouter la requête actuelle
        self.requests[client_id].append(now)


# Instance globale
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)