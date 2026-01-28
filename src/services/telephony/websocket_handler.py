
# ========================================
# src/services/telephony/websocket_handler.py
# ========================================
"""Handler WebSocket pour Twilio Media Streams."""
import json
import base64
import asyncio
from typing import Callable, Awaitable, Optional
from fastapi import WebSocket

from src.audio.stream_processor import AudioStreamProcessor


class TwilioWebSocketHandler:
    """Handler pour gérer les WebSocket Twilio Media Streams."""

    def __init__(self, websocket: WebSocket, call_id: str):
        """
        Initialiser le handler.

        Args:
            websocket: WebSocket FastAPI
            call_id: ID de l'appel
        """
        self.websocket = websocket
        self.call_id = call_id
        self.stream_sid: Optional[str] = None
        self.is_connected = False

        # Processeur audio
        self.audio_processor = AudioStreamProcessor(call_id)

        # Callbacks
        self.on_start_callback: Optional[Callable] = None
        self.on_audio_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None

    def set_callbacks(
            self,
            on_start: Callable[[dict], Awaitable[None]] = None,
            on_audio: Callable[[bytes], Awaitable[None]] = None,
            on_stop: Callable[[dict], Awaitable[None]] = None,
    ):
        """
        Définir les callbacks.

        Args:
            on_start: Callback au démarrage
            on_audio: Callback pour chaque chunk audio
            on_stop: Callback à l'arrêt
        """
        self.on_start_callback = on_start
        self.on_audio_callback = on_audio
        self.on_stop_callback = on_stop

    async def handle_connection(self):
        """Gérer la connexion WebSocket."""
        try:
            while True:
                # Recevoir message
                message = await self.websocket.receive_text()
                data = json.loads(message)

                event = data.get("event")

                if event == "start":
                    await self._handle_start(data)

                elif event == "media":
                    await self._handle_media(data)

                elif event == "stop":
                    await self._handle_stop(data)
                    break

                elif event == "mark":
                    # Mark events (optionnel)
                    pass

        except Exception as e:
            print(f"❌ Erreur WebSocket handler: {e}")
            raise

    async def _handle_start(self, data: dict):
        """
        Gérer l'événement START.

        Args:
            data: Données de l'événement
        """
        stream = data.get("start", {})
        self.stream_sid = stream.get("streamSid")

        print(f"📞 WebSocket START - Stream: {self.stream_sid}")

        self.is_connected = True

        # Démarrer le processeur audio
        await self.audio_processor.start()

        # Callback
        if self.on_start_callback:
            await self.on_start_callback(data)

    async def _handle_media(self, data: dict):
        """
        Gérer les chunks audio.

        Args:
            data: Données media
        """
        media = data.get("media", {})
        payload = media.get("payload")

        if payload:
            # Traiter avec le processeur audio
            await self.audio_processor.process_audio_chunk(payload)

            # Décoder pour callback
            if self.on_audio_callback:
                from src.audio.format_converter import AudioFormatConverter

                converter = AudioFormatConverter()
                audio_bytes = converter.decode_base64_audio(payload)
                audio_pcm = converter.mulaw_to_pcm(audio_bytes)

                await self.on_audio_callback(audio_pcm)

    async def _handle_stop(self, data: dict):
        """
        Gérer l'événement STOP.

        Args:
            data: Données de l'événement
        """
        print(f"📵 WebSocket STOP - Stream: {self.stream_sid}")

        self.is_connected = False

        # Arrêter le processeur audio
        recording_path = await self.audio_processor.stop()
        print(f"🎙️  Enregistrement sauvegardé: {recording_path}")

        # Callback
        if self.on_stop_callback:
            await self.on_stop_callback(data)

    async def send_audio(self, audio_data: bytes):
        """
        Envoyer de l'audio vers Twilio.

        Args:
            audio_data: Audio en PCM
        """
        if not self.is_connected:
            print("⚠️  WebSocket non connecté")
            return

        try:
            from src.audio.format_converter import AudioFormatConverter

            converter = AudioFormatConverter()

            # Convertir PCM vers mu-law
            mulaw_audio = converter.pcm_to_mulaw(audio_data)

            # Encoder en base64
            audio_base64 = converter.encode_base64_audio(mulaw_audio)

            # Message Twilio
            message = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {"payload": audio_base64},
            }

            await self.websocket.send_json(message)

        except Exception as e:
            print(f"❌ Erreur envoi audio: {e}")

    async def send_mark(self, name: str):
        """
        Envoyer un mark event.

        Args:
            name: Nom du mark
        """
        if not self.is_connected:
            return

        message = {"event": "mark", "streamSid": self.stream_sid, "mark": {"name": name}}

        await self.websocket.send_json(message)

    async def clear_buffer(self):
        """Vider le buffer audio."""
        message = {"event": "clear", "streamSid": self.stream_sid}

        await self.websocket.send_json(message)