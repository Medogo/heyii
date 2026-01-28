
# ========================================
# src/integrations/notifications/sms.py
# ========================================
"""Service d'envoi de SMS via Twilio."""
from twilio.rest import Client


class SMSService:
    """Service d'envoi de SMS."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """
        Initialiser le service SMS.

        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            from_number: Numéro d'envoi
        """
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    async def send_sms(self, to: str, body: str) -> bool:
        """
        Envoyer un SMS.

        Args:
            to: Numéro destinataire
            body: Corps du message

        Returns:
            True si envoyé
        """
        try:
            message = self.client.messages.create(
                from_=self.from_number, to=to, body=body
            )

            print(f"✅ SMS envoyé: {message.sid}")
            return True

        except Exception as e:
            print(f"❌ Erreur envoi SMS: {e}")
            return False

    async def send_order_confirmation(
            self, to: str, order_id: str, total_amount: float
    ) -> bool:
        """
        Envoyer une confirmation de commande par SMS.

        Args:
            to: Numéro destinataire
            order_id: ID commande
            total_amount: Montant

        Returns:
            True si succès
        """
        body = f"Commande {order_id} confirmée ! Montant: {total_amount:.2f}€. Merci!"

        return await self.send_sms(to, body)
