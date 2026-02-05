
# ========================================
# src/integrations/notifications/sms.py
# ========================================
"""Service d'envoi de SMS."""
# Twilio removed - implement alternative SMS service if needed


class SMSService:
    """Service d'envoi de SMS."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """
        Initialiser le service SMS.

        Args:
            account_sid: Account SID (deprecated - Twilio removed)
            auth_token: Auth Token (deprecated - Twilio removed)
            from_number: Numéro d'envoi
        """
        # Twilio removed - implement alternative service
        self.from_number = from_number
        print("⚠️  SMS Service: Twilio removed, implement alternative service")

    async def send_sms(self, to: str, body: str) -> bool:
        """
        Envoyer un SMS.

        Args:
            to: Numéro destinataire
            body: Corps du message

        Returns:
            True si envoyé
        """
        # Twilio removed - implement alternative service
        print(f"⚠️  SMS not sent (Twilio removed): {to}")
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
