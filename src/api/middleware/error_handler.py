
# ========================================
# src/api/middleware/error_handler.py
# ========================================
"""Middleware de gestion d'erreurs."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import settings


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Gérer les exceptions HTTP.

    Args:
        request: Requête
        exc: Exception

    Returns:
        JSON Response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Gérer les erreurs de validation.

    Args:
        request: Requête
        exc: Exception de validation

    Returns:
        JSON Response
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Erreur de validation",
            "details": exc.errors(),
            "path": request.url.path,
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Gérer les exceptions générales.

    Args:
        request: Requête
        exc: Exception

    Returns:
        JSON Response
    """
    print(f"💥 Erreur non gérée: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Erreur interne du serveur",
            "details": str(exc) if settings.app_debug else "Erreur interne",
            "path": request.url.path,
        },
    )


# Dict des handlers
exception_handlers = {
    StarletteHTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    Exception: general_exception_handler,
}