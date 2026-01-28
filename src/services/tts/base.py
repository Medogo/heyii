

# ========================================
# src/services/tts/base.py
# ========================================
"""Interface de base pour les services TTS."""
from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseTTSClient(ABC):
    """Interface de base pour les clients TTS."""

    @abstractmethod
    async def text_to_speech_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Convertir texte en audio (streaming)."""
        pass

    @abstractmethod
    async def text_to_speech(self, text: str) -> bytes:
        """Convertir texte en audio (complet)."""
        pass
