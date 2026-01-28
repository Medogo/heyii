"""Client Deepgram pour Speech-to-Text."""
import asyncio
from typing import Callable, Awaitable
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)

from src.core.config import settings


class DeepgramSTTClient:
    """Client pour Deepgram STT en streaming."""

    def __init__(self):
        """Initialiser le client Deepgram."""
        config = DeepgramClientOptions(
            api_key=settings.deepgram_api_key,
        )
        self.client = DeepgramClient("", config)
        self.connection = None
        self.is_connected = False

    async def start_streaming(
        self,
        on_transcript_callback: Callable[[str, bool, float], Awaitable[None]],
    ):
        """
        Démarrer le streaming STT.

        Args:
            on_transcript_callback: Fonction async appelée avec (transcript, is_final, confidence)
        """
        try:
            # Créer la connexion WebSocket
            self.connection = self.client.listen.asyncwebsocket.v("1")

            # Définir les callbacks
            async def on_message(self, result, **kwargs):
                """Callback pour les messages de transcription."""
                sentence = result.channel.alternatives[0].transcript
                is_final = result.is_final
                confidence = result.channel.alternatives[0].confidence

                if len(sentence) > 0:
                    await on_transcript_callback(sentence, is_final, confidence)

            async def on_metadata(self, metadata, **kwargs):
                """Callback pour les métadonnées."""
                print(f"📊 Deepgram metadata: {metadata}")

            async def on_error(self, error, **kwargs):
                """Callback pour les erreurs."""
                print(f"❌ Deepgram error: {error}")

            async def on_close(self, close, **kwargs):
                """Callback pour la fermeture."""
                print(f"🔌 Deepgram connection closed: {close}")
                self.is_connected = False

            # Enregistrer les callbacks
            self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            self.connection.on(LiveTranscriptionEvents.Error, on_error)
            self.connection.on(LiveTranscriptionEvents.Close, on_close)

            # Options de transcription
            options = LiveOptions(
                model=settings.deepgram_model,
                language=settings.deepgram_language,
                smart_format=True,
                interim_results=True,
                punctuate=True,
                profanity_filter=False,
                diarize=False,
                vad_events=True,
            )

            # Démarrer la connexion
            if await self.connection.start(options):
                print("✅ Deepgram STT connecté")
                self.is_connected = True
            else:
                print("❌ Échec connexion Deepgram")
                raise Exception("Failed to connect to Deepgram")

        except Exception as e:
            print(f"❌ Erreur démarrage Deepgram: {e}")
            raise

    async def send_audio(self, audio_chunk: bytes):
        """
        Envoyer un chunk audio au service STT.

        Args:
            audio_chunk: Données audio en bytes
        """
        if self.connection and self.is_connected:
            try:
                self.connection.send(audio_chunk)
            except Exception as e:
                print(f"❌ Erreur envoi audio: {e}")
        else:
            print("⚠️  Connexion Deepgram non établie")

    async def close(self):
        """Fermer la connexion."""
        if self.connection:
            try:
                await self.connection.finish()
                print("🔌 Deepgram STT déconnecté")
            except Exception as e:
                print(f"❌ Erreur fermeture Deepgram: {e}")
            finally:
                self.is_connected = False
                self.connection = None

    def is_ready(self) -> bool:
        """Vérifier si le client est prêt."""
        return self.is_connected and self.connection is not None