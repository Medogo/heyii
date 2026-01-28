

# ========================================
# src/api/middleware/logging.py
# ========================================
"""Middleware de logging."""
import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger les requêtes."""

    async def dispatch(self, request: Request, call_next):
        """
        Traiter la requête.

        Args:
            request: Requête
            call_next: Prochain middleware

        Returns:
            Response
        """
        start_time = time.time()

        # Informations de la requête
        request_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", ""),
        }

        # Traiter la requête
        try:
            response = await call_next(request)

            # Calculer le temps de traitement
            process_time = time.time() - start_time

            # Log de la réponse
            response_log = {
                **request_log,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
            }

            # Logger selon le niveau
            if response.status_code >= 500:
                print(f"❌ ERROR: {json.dumps(response_log)}")
            elif response.status_code >= 400:
                print(f"⚠️  WARNING: {json.dumps(response_log)}")
            else:
                print(f"✅ INFO: {json.dumps(response_log)}")

            # Ajouter le header de temps de traitement
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            process_time = time.time() - start_time

            error_log = {
                **request_log,
                "error": str(e),
                "process_time": f"{process_time:.3f}s",
            }

            print(f"💥 EXCEPTION: {json.dumps(error_log)}")
            raise

