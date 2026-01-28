"""Services de téléphonie Twilio."""

# ========================================
# src/services/telephony/twilio_client.py
# ========================================
"""Client Twilio pour la gestion des appels."""
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from typing import Dict, Any, Optional

from src.core.config import settings


class TwilioClient:
    """Client Twilio pour téléphonie."""

    def __init__(self):
        """Initialiser le client Twilio."""
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.phone_number = settings.twilio_phone_number

        self.client = Client(self.account_sid, self.auth_token)

    def create_call(self, to: str, from_: str = None, url: str = None) -> Dict[str, Any]:
        """
        Créer un appel sortant.

        Args:
            to: Numéro destinataire
            from_: Numéro émetteur (par défaut celui configuré)
            url: URL TwiML ou WebSocket

        Returns:
            Informations de l'appel
        """
        try:
            call = self.client.calls.create(
                to=to,
                from_=from_ or self.phone_number,
                url=url or "http://demo.twilio.com/docs/voice.xml",
            )

            print(f"📞 Appel créé: {call.sid}")

            return {
                "call_sid": call.sid,
                "status": call.status,
                "to": call.to,
                "from": call.from_,
            }

        except Exception as e:
            print(f"❌ Erreur création appel: {e}")
            raise

    def get_call_status(self, call_sid: str) -> str:
        """
        Récupérer le statut d'un appel.

        Args:
            call_sid: SID de l'appel

        Returns:
            Status de l'appel
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return call.status

        except Exception as e:
            print(f"❌ Erreur récupération status: {e}")
            return "unknown"

    def end_call(self, call_sid: str) -> bool:
        """
        Terminer un appel.

        Args:
            call_sid: SID de l'appel

        Returns:
            True si succès
        """
        try:
            call = self.client.calls(call_sid).update(status="completed")
            print(f"📵 Appel terminé: {call_sid}")
            return True

        except Exception as e:
            print(f"❌ Erreur fin appel: {e}")
            return False

    def generate_twiml_connect_stream(
            self, websocket_url: str, custom_params: Dict[str, str] = None
    ) -> str:
        """
        Générer TwiML pour connecter à un WebSocket.

        Args:
            websocket_url: URL du WebSocket
            custom_params: Paramètres personnalisés

        Returns:
            XML TwiML
        """
        response = VoiceResponse()

        # Message de bienvenue (optionnel)
        # response.say("Connexion en cours...", language='fr-FR')

        # Connecter au WebSocket
        connect = response.connect()
        stream = connect.stream(url=websocket_url)

        # Ajouter des paramètres personnalisés
        if custom_params:
            for key, value in custom_params.items():
                stream.parameter(name=key, value=value)

        return str(response)

    def generate_twiml_say(self, text: str, voice: str = "Polly.Lea") -> str:
        """
        Générer TwiML pour dire du texte.

        Args:
            text: Texte à dire
            voice: Voix à utiliser

        Returns:
            XML TwiML
        """
        response = VoiceResponse()
        response.say(text, language="fr-FR", voice=voice)

        return str(response)

    def send_sms(self, to: str, body: str, from_: str = None) -> Dict[str, Any]:
        """
        Envoyer un SMS.

        Args:
            to: Numéro destinataire
            body: Corps du message
            from_: Numéro émetteur

        Returns:
            Informations du message
        """
        try:
            message = self.client.messages.create(
                to=to, from_=from_ or self.phone_number, body=body
            )

            print(f"📱 SMS envoyé: {message.sid}")

            return {
                "message_sid": message.sid,
                "status": message.status,
                "to": message.to,
            }

        except Exception as e:
            print(f"❌ Erreur envoi SMS: {e}")
            raise

    def get_call_recordings(self, call_sid: str) -> list:
        """
        Récupérer les enregistrements d'un appel.

        Args:
            call_sid: SID de l'appel

        Returns:
            Liste des enregistrements
        """
        try:
            recordings = self.client.recordings.list(call_sid=call_sid)

            return [
                {
                    "recording_sid": rec.sid,
                    "duration": rec.duration,
                    "url": rec.uri,
                }
                for rec in recordings
            ]

        except Exception as e:
            print(f"❌ Erreur récupération recordings: {e}")
            return []


# Instance globale
twilio_client = TwilioClient()
