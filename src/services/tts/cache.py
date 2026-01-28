
# ========================================
# src/services/tts/cache.py
# ========================================
"""Cache pour le TTS."""
import hashlib
from typing import Optional
from src.utils.cache import cache


class TTSCache:
    """Cache pour les réponses TTS."""

    def __init__(self, ttl: int = 3600):
        """
        Initialiser le cache TTS.

        Args:
            ttl: Durée de vie en secondes
        """
        self.ttl = ttl
        self.prefix = "tts:"

    def _get_cache_key(self, text: str, voice_id: str) -> str:
        """
        Générer une clé de cache.

        Args:
            text: Texte
            voice_id: ID de la voix

        Returns:
            Clé de cache
        """
        hash_input = f"{text}:{voice_id}".encode("utf-8")
        text_hash = hashlib.md5(hash_input).hexdigest()
        return f"{self.prefix}{text_hash}"

    async def get(self, text: str, voice_id: str) -> Optional[bytes]:
        """
        Récupérer audio depuis le cache.

        Args:
            text: Texte
            voice_id: ID de la voix

        Returns:
            Audio en bytes ou None
        """
        key = self._get_cache_key(text, voice_id)
        cached = await cache.get(key)

        if cached:
            print(f"✅ TTS Cache HIT: {text[:30]}...")
            # Décoder depuis base64 si nécessaire
            import base64

            return base64.b64decode(cached)

        return None

    async def set(self, text: str, voice_id: str, audio_data: bytes):
        """
        Mettre en cache l'audio.

        Args:
            text: Texte
            voice_id: ID de la voix
            audio_data: Audio en bytes
        """
        key = self._get_cache_key(text, voice_id)

        # Encoder en base64 pour stockage
        import base64

        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        await cache.set(key, audio_base64, ttl=self.ttl)
        print(f"💾 TTS mis en cache: {text[:30]}...")


# Instance globale
tts_cache = TTSCache()
