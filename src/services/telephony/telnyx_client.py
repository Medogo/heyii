
# ========================================
# src/services/telephony/telnyx_client.py
# ========================================
"""Client Telnyx pour la téléphonie."""
import telnyx
import httpx
from typing import Optional, Dict, Any
from src.core.config import settings


class TelnyxClient:
    """Client pour gérer les appels et SMS via Telnyx."""

    def __init__(
            self,
            api_key: str = None,
            phone_number: str = None,
    ):
        """
        Initialiser le client Telnyx.

        Args:
            api_key: Clé API Telnyx
            phone_number: Numéro de téléphone Telnyx
        """
        self.api_key = api_key or settings.telnyx_api_key
        self.phone_number = phone_number or settings.telnyx_phone_number

        # Configurer Telnyx SDK
        telnyx.api_key = self.api_key

        # Base URL pour API REST
        self.base_url = "https://api.telnyx.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_call(
            self,
            to: str,
            from_: str = None,
            connection_id: str = None,
            webhook_url: str = None,
    ) -> Dict[str, Any]:
        """
        Créer un appel sortant.

        Args:
            to: Numéro à appeler (format E.164: +229XXXXXXXX)
            from_: Numéro appelant (défaut: self.phone_number)
            connection_id: ID de connexion Telnyx
            webhook_url: URL webhook pour les événements d'appel

        Returns:
            Informations de l'appel
        """
        try:
            from_number = from_ or self.phone_number

            payload = {
                "to": to,
                "from": from_number,
                "connection_id": connection_id or settings.telnyx_connection_id,
            }

            if webhook_url:
                payload["webhook_url"] = webhook_url

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calls",
                    json=payload,
                    headers=self.headers,
                    timeout=30,
                )

                response.raise_for_status()
                result = response.json()

                call_data = result.get("data", {})

                print(f"✅ Appel créé: {call_data.get('call_control_id')}")

                return {
                    "call_id": call_data.get("call_control_id"),
                    "status": call_data.get("state"),
                    "to": to,
                    "from": from_number,
                }

        except Exception as e:
            print(f"❌ Erreur création appel Telnyx: {e}")
            raise

    async def answer_call(self, call_control_id: str, webhook_url: str = None) -> bool:
        """
        Répondre à un appel entrant.

        Args:
            call_control_id: ID de contrôle de l'appel
            webhook_url: URL webhook

        Returns:
            True si succès
        """
        try:
            payload = {}
            if webhook_url:
                payload["webhook_url"] = webhook_url

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calls/{call_control_id}/actions/answer",
                    json=payload,
                    headers=self.headers,
                    timeout=10,
                )

                response.raise_for_status()
                print(f"✅ Appel répondu: {call_control_id}")
                return True

        except Exception as e:
            print(f"❌ Erreur réponse appel: {e}")
            return False

    async def hangup_call(self, call_control_id: str) -> bool:
        """
        Raccrocher un appel.

        Args:
            call_control_id: ID de contrôle de l'appel

        Returns:
            True si succès
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calls/{call_control_id}/actions/hangup",
                    headers=self.headers,
                    timeout=10,
                )

                response.raise_for_status()
                print(f"✅ Appel raccroché: {call_control_id}")
                return True

        except Exception as e:
            print(f"❌ Erreur raccrochage: {e}")
            return False

    async def stream_audio_start(
            self,
            call_control_id: str,
            stream_url: str,
            stream_track: str = "both",
    ) -> bool:
        """
        Démarrer le streaming audio (WebSocket).

        Args:
            call_control_id: ID de contrôle de l'appel
            stream_url: URL WebSocket (wss://...)
            stream_track: 'inbound', 'outbound', ou 'both'

        Returns:
            True si succès
        """
        try:
            payload = {
                "stream_url": stream_url,
                "stream_track": stream_track,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calls/{call_control_id}/actions/streaming_start",
                    json=payload,
                    headers=self.headers,
                    timeout=10,
                )

                response.raise_for_status()
                print(f"✅ Streaming démarré: {call_control_id}")
                return True

        except Exception as e:
            print(f"❌ Erreur démarrage streaming: {e}")
            return False

    async def stream_audio_stop(self, call_control_id: str) -> bool:
        """
        Arrêter le streaming audio.

        Args:
            call_control_id: ID de contrôle de l'appel

        Returns:
            True si succès
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calls/{call_control_id}/actions/streaming_stop",
                    headers=self.headers,
                    timeout=10,
                )

                response.raise_for_status()
                print(f"✅ Streaming arrêté: {call_control_id}")
                return True

        except Exception as e:
            print(f"❌ Erreur arrêt streaming: {e}")
            return False

    async def send_sms(
            self,
            to: str,
            text: str,
            from_: str = None,
    ) -> Optional[str]:
        """
        Envoyer un SMS.

        Args:
            to: Numéro destinataire
            text: Texte du message
            from_: Numéro expéditeur

        Returns:
            ID du message
        """
        try:
            payload = {
                "to": to,
                "text": text,
                "from": from_ or self.phone_number,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=self.headers,
                    timeout=10,
                )

                response.raise_for_status()
                result = response.json()

                message_data = result.get("data", {})
                message_id = message_data.get("id")

                print(f"✅ SMS envoyé: {message_id}")
                return message_id

        except Exception as e:
            print(f"❌ Erreur envoi SMS: {e}")
            return None

    async def get_call_status(self, call_control_id: str) -> Dict[str, Any]:
        """
        Récupérer le statut d'un appel.

        Args:
            call_control_id: ID de contrôle de l'appel

        Returns:
            Informations de l'appel
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calls/{call_control_id}",
                    headers=self.headers,
                    timeout=10,
                )

                response.raise_for_status()
                result = response.json()

                return result.get("data", {})

        except Exception as e:
            print(f"❌ Erreur récupération statut: {e}")
            return {}

    def generate_twiml_for_stream(self, websocket_url: str) -> str:
        """
        Générer TwiML pour streaming (compatible Telnyx).

        Args:
            websocket_url: URL WebSocket

        Returns:
            XML TwiML
        """
        # Telnyx n'utilise pas TwiML mais des commandes JSON
        # Cette méthode est gardée pour compatibilité
        return f"""
        {{
            "stream_url": "{websocket_url}",
            "stream_track": "both"
        }}
        """