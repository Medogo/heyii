"""Middleware pour l'API FastAPI."""

# ========================================
# src/api/middleware/auth.py
# ========================================
"""Middleware d'authentification."""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime, timedelta

from src.core.config import settings

security = HTTPBearer()


class AuthMiddleware:
    """Middleware d'authentification JWT."""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm

    def create_access_token(
            self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Créer un token JWT.

        Args:
            data: Données à encoder
            expires_delta: Durée de validité

        Returns:
            Token JWT
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.jwt_expiration_minutes
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """
        Vérifier un token JWT.

        Args:
            token: Token à vérifier

        Returns:
            Payload décodé

        Raises:
            HTTPException: Si token invalide
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expiré",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(
            self, credentials: HTTPAuthorizationCredentials
    ) -> dict:
        """
        Récupérer l'utilisateur courant depuis le token.

        Args:
            credentials: Credentials HTTP

        Returns:
            User data
        """
        token = credentials.credentials
        payload = self.verify_token(token)
        return payload


auth_middleware = AuthMiddleware()
