"""Modules de traitement audio."""

# ========================================
# src/audio/buffer.py
# ========================================
"""Buffer audio circulaire pour streaming."""
import asyncio
from collections import deque
from typing import Optional


class AudioBuffer:
    """Buffer circulaire pour chunks audio."""

    def __init__(self, max_size: int = 100):
        """
        Initialiser le buffer.

        Args:
            max_size: Taille maximale du buffer
        """
        self.buffer = deque(maxlen=max_size)
        self.lock = asyncio.Lock()

    async def add(self, audio_chunk: bytes):
        """
        Ajouter un chunk audio.

        Args:
            audio_chunk: Données audio
        """
        async with self.lock:
            self.buffer.append(audio_chunk)

    async def get(self) -> Optional[bytes]:
        """
        Récupérer le prochain chunk.

        Returns:
            Chunk audio ou None
        """
        async with self.lock:
            if self.buffer:
                return self.buffer.popleft()
            return None

    async def get_all(self) -> bytes:
        """
        Récupérer tous les chunks et vider le buffer.

        Returns:
            Audio complet
        """
        async with self.lock:
            audio = b"".join(self.buffer)
            self.buffer.clear()
            return audio

    def size(self) -> int:
        """Taille actuelle du buffer."""
        return len(self.buffer)

    def is_empty(self) -> bool:
        """Vérifier si le buffer est vide."""
        return len(self.buffer) == 0

    async def clear(self):
        """Vider le buffer."""
        async with self.lock:
            self.buffer.clear()



