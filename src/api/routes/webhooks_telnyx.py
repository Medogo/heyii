
# ========================================
# src/api/routes/webhooks_telnyx.py
# ========================================
"""Routes webhook Telnyx."""
from fastapi import APIRouter, Request, WebSocket
from src.services.telephony.telnyx_client import TelnyxClient
from src.services.telephony.telnyx_websocket import TelnyxWebSocketHandler

router = APIRouter(prefix="/webhooks/telnyx", tags=["telnyx"])


@router.post("/call-control")
async def telnyx_webhook(request: Request):
    """
    Webhook pour événements Telnyx.

    Événements reçus:
    - call.initiated
    - call.answered
    - call.hangup
    - call.machine.detection.ended
    """
    try:
        data = await request.json()
        event_type = data.get("data", {}).get("event_type")

        print(f"📞 Telnyx event: {event_type}")

        # Traiter selon le type d'événement
        if event_type == "call.initiated":
            # Appel initié
            pass
        elif event_type == "call.answered":
            # Appel répondu
            pass
        elif event_type == "call.hangup":
            # Appel raccroché
            pass

        return {"status": "ok"}

    except Exception as e:
        print(f"❌ Erreur webhook Telnyx: {e}")
        return {"status": "error", "message": str(e)}


@router.websocket("/stream")
async def telnyx_stream(websocket: WebSocket):
    """WebSocket pour streaming audio Telnyx."""

    async def on_audio(audio_data: bytes):
        # Traiter l'audio reçu
        print(f"🎤 Audio reçu: {len(audio_data)} bytes")

    async def on_start(call_control_id: str):
        print(f"▶️  Stream démarré: {call_control_id}")

    async def on_stop(call_control_id: str):
        print(f"⏹️  Stream arrêté: {call_control_id}")

    handler = TelnyxWebSocketHandler(
        on_audio=on_audio,
        on_start=on_start,
        on_stop=on_stop,
    )

    await handler.handle_connection(websocket)