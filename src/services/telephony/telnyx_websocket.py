
# ========================================
# src/services/telephony/telnyx_websocket.py
# ========================================
"""Gestionnaire WebSocket Telnyx."""
import json
import base64
import asyncio
from typing import Callable, Optional
from fastapi import WebSocket


class TelnyxWebSocketHandler:
    """Gestionnaire de WebSocket pour Telnyx."""

    def __init__(
            self,
            on_audio: Optional[Callable] = None,
            on_start: Optional[Callable] = None,
            on_stop: Optional[Callable] = None,
    ):
        """
        Initialiser le handler.

        Args:
            on_audio: Callback pour audio reçu
            on_start: Callback au démarrage
            on_stop: Callback à l'arrêt
        """
        self.on_audio = on_audio
        self.on_start = on_start
        self.on_stop = on_stop

        self.websocket: Optional[WebSocket] = None
        self.call_control_id: Optional[str] = None
        self.stream_id: Optional[str] = None

    async def handle_connection(self, websocket: WebSocket):
        """
        Gérer la connexion WebSocket Telnyx.

        Args:
            websocket: WebSocket FastAPI
        """
        await websocket.accept()
        self.websocket = websocket

        try:
            async for message in websocket.iter_text():
                await self._handle_message(message)

        except Exception as e:
            print(f"❌ Erreur WebSocket Telnyx: {e}")
        finally:
            if self.on_stop:
                await self.on_stop(self.call_control_id)

    async def _handle_message(self, message: str):
        """
        Traiter un message WebSocket.

        Args:
            message: Message JSON
        """
        try:
            data = json.loads(message)
            event_type = data.get("event_type")

            # Stream started
            if event_type == "streaming.started":
                self.call_control_id = data.get("call_control_id")
                self.stream_id = data.get("stream_id")

                print(f"🎙️  Stream démarré: {self.stream_id}")

                if self.on_start:
                    await self.on_start(self.call_control_id)

            # Audio data
            elif event_type == "audio":
                payload = data.get("payload", {})
                audio_base64 = payload.get("payload")

                if audio_base64 and self.on_audio:
                    # Telnyx envoie en base64
                    audio_bytes = base64.b64decode(audio_base64)
                    await self.on_audio(audio_bytes)

            # Stream stopped
            elif event_type == "streaming.stopped":
                print(f"🛑 Stream arrêté: {self.stream_id}")

                if self.on_stop:
                    await self.on_stop(self.call_control_id)

        except Exception as e:
            print(f"❌ Erreur traitement message: {e}")

    async def send_audio(self, audio_data: bytes):
        """
        Envoyer de l'audio au stream.

        Args:
            audio_data: Audio PCM
        """
        if not self.websocket:
            return

        try:
            # Encoder en base64
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            message = {
                "event_type": "audio",
                "stream_id": self.stream_id,
                "payload": {
                    "payload": audio_base64,
                },
            }

            await self.websocket.send_text(json.dumps(message))

        except Exception as e:
            print(f"❌ Erreur envoi audio: {e}")

    async def send_mark(self, mark_name: str):
        """
        Envoyer un marqueur.

        Args:
            mark_name: Nom du marqueur
        """
        if not self.websocket:
            return

        try:
            message = {
                "event_type": "mark",
                "stream_id": self.stream_id,
                "mark_name": mark_name,
            }

            await self.websocket.send_text(json.dumps(message))

        except Exception as e:
            print(f"❌ Erreur envoi mark: {e}")