
# ========================================
# src/demo/notification_handler.py
# ========================================
"""Gestionnaire de notifications pour le mode démo."""
from typing import List, Dict, Any
from src.integrations.notifications.brevo_email import BrevoEmailService
from src.services.telephony.twilio_client import TwilioClient
from src.core.config import settings


class DemoNotificationHandler:
    """Gestionnaire de notifications pour le mode démo."""

    def __init__(self):
        """Initialiser le handler."""
        # Email via Brevo
        self.email_service = BrevoEmailService(
            api_key=settings.brevo_api_key,
            sender_email=settings.brevo_sender_email,
            sender_name=settings.brevo_sender_name,
        )

        # WhatsApp/SMS via Twilio
        self.twilio_client = TwilioClient()

    async def send_order_notification(
            self,
            order_id: str,
            pharmacy_name: str,
            items: List[Dict[str, Any]],
            total_amount: float,
            via_email: bool = True,
            via_whatsapp: bool = False,
            email_to: List[str] = None,
            whatsapp_to: str = None,
    ) -> Dict[str, bool]:
        """
        Envoyer notification de commande par email et/ou WhatsApp.

        Args:
            order_id: ID de la commande
            pharmacy_name: Nom de la pharmacie
            items: Items de la commande
            total_amount: Montant total
            via_email: Envoyer par email
            via_whatsapp: Envoyer par WhatsApp
            email_to: Emails destinataires
            whatsapp_to: Numéro WhatsApp

        Returns:
            Status d'envoi
        """
        results = {"email": False, "whatsapp": False}

        # Formater les items
        items_text = self._format_items(items)

        # EMAIL
        if via_email and email_to:
            try:
                success = await self.email_service.send_order_notification(
                    order_id=order_id,
                    pharmacy_name=pharmacy_name,
                    total_amount=total_amount,
                    items_count=len(items),
                    to_emails=email_to,
                )
                results["email"] = success
            except Exception as e:
                print(f"❌ Erreur envoi email: {e}")

        # WHATSAPP
        if via_whatsapp and whatsapp_to:
            try:
                # WhatsApp via Twilio
                message_body = f"""
🛒 *Nouvelle Commande HEYI* (MODE DÉMO)

📋 Commande: {order_id}
🏥 Pharmacie: {pharmacy_name}
💰 Montant: {total_amount:.2f} €

📦 Articles:
{items_text}

✅ Commande reçue via l'agent IA vocal
                """.strip()

                # Format WhatsApp Twilio: whatsapp:+xxxxxx
                whatsapp_number = f"whatsapp:{whatsapp_to}"

                result = self.twilio_client.send_sms(
                    to=whatsapp_number,
                    body=message_body,
                )

                results["whatsapp"] = result is not None

            except Exception as e:
                print(f"❌ Erreur envoi WhatsApp: {e}")

        return results

    def _format_items(self, items: List[Dict[str, Any]]) -> str:
        """
        Formater la liste d'items.

        Args:
            items: Items de commande

        Returns:
            Texte formaté
        """
        lines = []
        for i, item in enumerate(items, 1):
            product_name = item.get("product_name", "Produit")
            quantity = item.get("quantity", 0)
            unit = item.get("unit", "unités")
            lines.append(f"{i}. {quantity} {unit} - {product_name}")

        return "\n".join(lines)

