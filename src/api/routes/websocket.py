"""WebSocket pour Twilio Media Streams."""
import json
import base64
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import get_db
from src.agent.orchestrator import AgentOrchestrator
from src.agent.call_manager import call_manager
from src.services.stt.deepgram_client import DeepgramSTTClient
from src.services.llm.openai_client import OpenAIClient
from src.services.tts.elevenlabs_client import ElevenLabsTTSClient
from src.services.vector_db.qdrant_client import qdrant_client
from src.business.product_service import ProductService
from src.business.order_service import OrderService
from src.data.repositories.call_repository import CallRepository


router = APIRouter(tags=["WebSocket"])


class TwilioWebSocketHandler:
    """Gestionnaire WebSocket pour Twilio."""

    def __init__(self, websocket: WebSocket, db: AsyncSession):
        self.websocket = websocket
        self.db = db
        self.call_id: str | None = None
        self.stream_sid: str | None = None

        # Initialiser les services
        self.stt_client = DeepgramSTTClient()
        self.llm_client = OpenAIClient()
        self.tts_client = ElevenLabsTTSClient()

        # Services métier
        self.product_service = ProductService(db)
        self.order_service = OrderService(db)

        # Orchestrateur
        self.orchestrator = AgentOrchestrator(
            stt_client=self.stt_client,
            llm_client=self.llm_client,
            tts_client=self.tts_client,
            qdrant_client=qdrant_client,
            product_service=self.product_service,
            order_service=self.order_service,
        )

    async def handle_start(self, data: dict):
        """Gérer l'événement START de Twilio."""
        stream = data.get("start", {})
        self.stream_sid = stream.get("streamSid")
        self.call_id = stream.get("callSid")

        call_sid = stream.get("callSid")
        custom_parameters = stream.get("customParameters", {})

        print(f"📞 WebSocket START - CallSid: {call_sid}")
        print(f"   Stream: {self.stream_sid}")

        # Démarrer l'appel
        call_repo = CallRepository(self.db)
        phone_number = custom_parameters.get("From", "unknown")

        await call_manager.start_call(
            call_id=call_sid,
            phone_number=phone_number,
            call_repository=call_repo
        )

        # Démarrer le STT
        async def on_transcript(transcript: str, is_final: bool):
            """Callback pour la transcription."""
            # Simuler confidence (Deepgram devrait le fournir)
            confidence = 0.95 if is_final else 0.70

            response_text = await self.orchestrator.handle_transcript(
                call_id=call_sid,
                transcript=transcript,
                is_final=is_final,
                confidence=confidence
            )

            if response_text and is_final:
                # Envoyer la réponse TTS vers Twilio
                await self.send_tts_response(response_text)

        await self.stt_client.start_streaming(on_transcript)

        # Message d'accueil
        greeting = await self.orchestrator.handle_call_start(call_sid)
        await self.send_tts_response(greeting)

    async def handle_media(self, data: dict):
        """Gérer les chunks audio entrants."""
        media = data.get("media", {})
        payload = media.get("payload")

        if payload:
            # Décoder l'audio (mulaw base64)
            audio_bytes = base64.b64decode(payload)

            # Envoyer au STT
            await self.orchestrator.handle_audio_chunk(
                self.call_id,
                audio_bytes
            )

    async def handle_stop(self, data: dict):
        """Gérer l'événement STOP."""
        print(f"📵 WebSocket STOP - CallSid: {self.call_id}")

        # Terminer l'appel
        call_repo = CallRepository(self.db)
        await call_manager.end_call(self.call_id, call_repo)

        # Fermer le STT
        await self.stt_client.close()

    async def send_tts_response(self, text: str):
        """Envoyer une réponse TTS vers Twilio."""
        print(f"🔊 TTS: {text}")

        # Générer l'audio avec ElevenLabs
        audio_chunks = []
        async for chunk in self.tts_client.text_to_speech_stream(text):
            audio_chunks.append(chunk)

        # Combiner les chunks
        full_audio = b"".join(audio_chunks)

        # Encoder en base64 mulaw pour Twilio
        audio_base64 = base64.b64encode(full_audio).decode("utf-8")

        # Envoyer vers Twilio
        message = {
            "event": "media",
            "streamSid": self.stream_sid,
            "media": {
                "payload": audio_base64
            }
        }

        await self.websocket.send_json(message)


@router.websocket("/ws/voice")
async def websocket_voice_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint WebSocket pour Twilio Voice."""

    await websocket.accept()
    print("✅ WebSocket connecté")

    handler = TwilioWebSocketHandler(websocket, db)

    try:
        while True:
            # Recevoir message de Twilio
            message = await websocket.receive_text()
            data = json.loads(message)

            event = data.get("event")

            if event == "start":
                await handler.handle_start(data)

            elif event == "media":
                await handler.handle_media(data)

            elif event == "stop":
                await handler.handle_stop(data)
                break

            elif event == "mark":
                # Mark events (optionnel)
                pass

    except WebSocketDisconnect:
        print("❌ WebSocket déconnecté")

        if handler.call_id:
            call_repo = CallRepository(db)
            await call_manager.end_call(
                handler.call_id,
                call_repo,
                status="disconnected"
            )

    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        await websocket.close()