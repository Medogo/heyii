"""Client ElevenLabs pour Text-to-Speech."""
from typing import AsyncGenerator
from elevenlabs import AsyncElevenLabs
from elevenlabs.types import VoiceSettings

from src.core.config import settings


class ElevenLabsTTSClient:
    """Client ElevenLabs TTS en streaming."""

    def __init__(self):
        """Initialiser le client ElevenLabs."""
        self.client = AsyncElevenLabs(api_key=settings.elevenlabs_api_key)
        self.voice_id = settings.elevenlabs_voice_id
        self.model_id = settings.elevenlabs_model

        # Settings de voix optimisés pour agent vocal
        self.voice_settings = VoiceSettings(
            stability=0.5,  # Naturel mais pas monotone
            similarity_boost=0.75,  # Fidélité à la voix
            style=0.0,  # Pas de style exagéré
            use_speaker_boost=True,  # Améliore la clarté
        )

    async def text_to_speech_stream(
        self, text: str
    ) -> AsyncGenerator[bytes, None]:
        """
        Convertir texte en audio (streaming).

        Args:
            text: Texte à convertir

        Yields:
            Chunks audio en bytes
        """
        try:
            print(f"🔊 TTS génération: {text[:50]}...")

            audio_stream = self.client.text_to_speech.convert_as_stream(
                voice_id=self.voice_id,
                text=text,
                model_id=self.model_id,
                voice_settings=self.voice_settings,
            )

            async for chunk in audio_stream:
                yield chunk

            print("✅ TTS généré avec succès")

        except Exception as e:
            print(f"❌ Erreur ElevenLabs TTS: {e}")
            # En cas d'erreur, on ne yield rien
            raise

    async def text_to_speech(self, text: str) -> bytes:
        """
        Convertir texte en audio (complet).

        Args:
            text: Texte à convertir

        Returns:
            Audio complet en bytes
        """
        try:
            print(f"🔊 TTS génération complète: {text[:50]}...")

            audio = await self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id=self.model_id,
                voice_settings=self.voice_settings,
            )

            print("✅ TTS généré avec succès")
            return audio

        except Exception as e:
            print(f"❌ Erreur ElevenLabs TTS: {e}")
            raise

    async def get_available_voices(self) -> list:
        """
        Récupérer les voix disponibles.

        Returns:
            Liste des voix disponibles
        """
        try:
            voices = await self.client.voices.get_all()
            return voices.voices

        except Exception as e:
            print(f"❌ Erreur récupération voix: {e}")
            return []

    async def get_voice_info(self, voice_id: str = None) -> dict:
        """
        Récupérer les infos d'une voix.

        Args:
            voice_id: ID de la voix (utilise celle par défaut si None)

        Returns:
            Informations de la voix
        """
        try:
            vid = voice_id or self.voice_id
            voice = await self.client.voices.get(vid)

            return {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
                "description": voice.description,
                "labels": voice.labels,
            }

        except Exception as e:
            print(f"❌ Erreur info voix: {e}")
            return {}

    def set_voice(self, voice_id: str):
        """
        Changer la voix utilisée.

        Args:
            voice_id: ID de la nouvelle voix
        """
        self.voice_id = voice_id
        print(f"🔊 Voix changée: {voice_id}")

    def update_voice_settings(
        self,
        stability: float = None,
        similarity_boost: float = None,
        style: float = None,
    ):
        """
        Mettre à jour les paramètres de voix.

        Args:
            stability: Stabilité (0.0 à 1.0)
            similarity_boost: Similarité (0.0 à 1.0)
            style: Style (0.0 à 1.0)
        """
        if stability is not None:
            self.voice_settings.stability = max(0.0, min(1.0, stability))

        if similarity_boost is not None:
            self.voice_settings.similarity_boost = max(
                0.0, min(1.0, similarity_boost)
            )

        if style is not None:
            self.voice_settings.style = max(0.0, min(1.0, style))

        print(f"🎛️  Paramètres voix mis à jour: {self.voice_settings}")