
# ========================================
# src/audio/stream_processor.py
# ========================================
"""Processeur de flux audio."""
import asyncio
from typing import Callable, Awaitable

from src.audio.buffer import AudioBuffer
from src.audio.vad import VAD
from src.audio.format_converter import AudioFormatConverter
from src.audio.recorder import AudioRecorder


class AudioStreamProcessor:
    """Processeur de flux audio."""

    def __init__(self, call_id: str):
        """
        Initialiser le processeur.

        Args:
            call_id: ID de l'appel
        """
        self.call_id = call_id
        self.buffer = AudioBuffer(max_size=200)
        self.vad = VAD(aggressiveness=2)
        self.converter = AudioFormatConverter()
        self.recorder = AudioRecorder()

        self.is_processing = False
        self.speech_detected = False

    async def start(self):
        """Démarrer le traitement."""
        self.is_processing = True
        self.recorder.start_recording(self.call_id)
        print(f"▶️  Stream processor démarré: {self.call_id}")

    async def stop(self) -> str:
        """
        Arrêter le traitement.

        Returns:
            Chemin du fichier audio
        """
        self.is_processing = False
        filename = self.recorder.stop_recording()
        await self.buffer.clear()
        print(f"⏹️  Stream processor arrêté: {self.call_id}")
        return filename

    async def process_audio_chunk(
            self, audio_chunk_base64: str, on_speech_callback: Callable = None
    ):
        """
        Traiter un chunk audio.

        Args:
            audio_chunk_base64: Audio encodé en base64
            on_speech_callback: Callback si parole détectée
        """
        if not self.is_processing:
            return

        # Décoder
        audio_bytes = self.converter.decode_base64_audio(audio_chunk_base64)

        # Convertir mu-law vers PCM
        pcm_audio = self.converter.mulaw_to_pcm(audio_bytes)

        # Ajouter au buffer
        await self.buffer.add(pcm_audio)

        # Enregistrer
        self.recorder.add_audio_chunk(pcm_audio)

        # VAD
        is_speech = self.vad.is_speech(pcm_audio)

        if is_speech and not self.speech_detected:
            self.speech_detected = True
            print("🎤 Parole détectée")

            if on_speech_callback:
                await on_speech_callback()

        elif not is_speech and self.speech_detected:
            # Fin de parole détectée
            print("🔇 Fin de parole")
            self.speech_detected = False

    async def get_audio_segment(self) -> bytes:
        """
        Récupérer un segment audio complet.

        Returns:
            Audio en bytes
        """
        return await self.buffer.get_all()