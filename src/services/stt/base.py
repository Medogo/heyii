"""Fichiers de base et utilitaires."""

# ========================================
# src/services/stt/base.py
# ========================================
"""Interface de base pour les services STT."""
from abc import ABC, abstractmethod
from typing import Callable, Awaitable
class BaseSTTClient(ABC):
    """Interface de base pour les clients STT."""

    @abstractmethod
    async def start_streaming(
            self, on_transcript_callback: Callable[[str, bool, float], Awaitable[None]]
    ):
        """Démarrer le streaming STT."""
        pass

    @abstractmethod
    async def send_audio(self, audio_chunk: bytes):
        """Envoyer un chunk audio."""
        pass

    @abstractmethod
    async def close(self):
        """Fermer la connexion."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Vérifier si le client est prêt."""
        pass





