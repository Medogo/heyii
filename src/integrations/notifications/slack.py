

# ========================================
# src/integrations/notifications/slack.py
# ========================================
"""Service de notifications Slack."""
import httpx
from typing import Dict, Any, List


class SlackService:
    """Service de notifications Slack."""

    def __init__(self, webhook_url: str):
        """
        Initialiser le service Slack.

        Args:
            webhook_url: URL du webhook Slack
        """
        self.webhook_url = webhook_url

    async def send_message(
            self,
            text: str,
            blocks: Optional[List[Dict[str, Any]]] = None,
            channel: Optional[str] = None,
    ) -> bool:
        """
        Envoyer un message Slack.

        Args:
            text: Texte du message
            blocks: Blocs Slack (optionnel)
            channel: Canal (optionnel)

        Returns:
            True si envoyé
        """
        try:
            payload = {"text": text}

            if blocks:
                payload["blocks"] = blocks

            if channel:
                payload["channel"] = channel

            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()

            print(f"✅ Message Slack envoyé")
            return True

        except Exception as e:
            print(f"❌ Erreur envoi Slack: {e}")
            return False

    async def send_order_alert(
            self, order_id: str, pharmacy_name: str, total_amount: float
    ) -> bool:
        """
        Envoyer une alerte de commande.

        Args:
            order_id: ID commande
            pharmacy_name: Nom pharmacie
            total_amount: Montant

        Returns:
            True si succès
        """
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🛒 Nouvelle commande"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Commande:*\n{order_id}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Pharmacie:*\n{pharmacy_name}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Montant:*\n{total_amount:.2f}€",
                    },
                ],
            },
        ]

        return await self.send_message(
            text=f"Nouvelle commande: {order_id}", blocks=blocks
        )

    async def send_validation_alert(
            self, order_id: str, reason: str, amount: float
    ) -> bool:
        """
        Envoyer une alerte de validation requise.

        Args:
            order_id: ID commande
            reason: Raison
            amount: Montant

        Returns:
            True si succès
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚠️ Validation requise",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Commande:*\n{order_id}"},
                    {"type": "mrkdwn", "text": f"*Raison:*\n{reason}"},
                    {"type": "mrkdwn", "text": f"*Montant:*\n{amount:.2f}€"},
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Voir commande"},
                        "url": f"https://dashboard.heyi.com/orders/{order_id}",
                    }
                ],
            },
        ]

        return await self.send_message(
            text=f"Validation requise: {order_id}", blocks=blocks
        )

    async def send_error_alert(self, error_message: str, call_id: str) -> bool:
        """
        Envoyer une alerte d'erreur.

        Args:
            error_message: Message d'erreur
            call_id: ID de l'appel

        Returns:
            True si succès
        """
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 Erreur système"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Appel:*\n{call_id}"},
                    {"type": "mrkdwn", "text": f"*Erreur:*\n{error_message}"},
                ],
            },
        ]

        return await self.send_message(
            text=f"Erreur système - {call_id}", blocks=blocks
        )