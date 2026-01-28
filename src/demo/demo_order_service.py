
# ========================================
# src/demo/demo_order_service.py
# ========================================
"""Service de commande pour le mode démo."""
from datetime import datetime
from typing import List, Dict, Any
from src.demo.mock_erp_client import MockERPClient
from src.demo.notification_handler import DemoNotificationHandler


class DemoOrderService:
    """Service de commande pour démo (sans ERP réel)."""

    def __init__(
            self,
            notification_emails: List[str] = None,
            notification_whatsapp: str = None,
    ):
        """
        Initialiser le service démo.

        Args:
            notification_emails: Emails pour notifications
            notification_whatsapp: Numéro WhatsApp pour notifications
        """
        self.mock_erp = MockERPClient()
        self.notifier = DemoNotificationHandler()

        # Configuration des notifications
        self.notification_emails = notification_emails or []
        self.notification_whatsapp = notification_whatsapp

    async def create_order(
            self,
            call_id: str,
            pharmacy_id: str,
            pharmacy_name: str,
            items: List[Dict[str, Any]],
            confidence: float,
    ) -> Dict[str, Any]:
        """
        Créer une commande en mode démo.

        Args:
            call_id: ID de l'appel
            pharmacy_id: ID pharmacie
            pharmacy_name: Nom pharmacie
            items: Items commandés
            confidence: Score de confiance

        Returns:
            Résultat de la commande
        """
        print(f"🎭 MODE DÉMO: Création commande pour {pharmacy_name}")

        # Calculer le total
        total_amount = sum(
            item.get("quantity", 0) * item.get("unit_price", 0)
            for item in items
        )

        # Préparer les données pour le mock ERP
        erp_data = {
            "pharmacy_id": pharmacy_id,
            "order_date": datetime.utcnow().isoformat(),
            "items": [
                {
                    "product_cip13": item.get("product_cip"),
                    "quantity": item.get("quantity"),
                    "unit_price": item.get("unit_price"),
                    "line_total": item.get("quantity", 0) * item.get("unit_price", 0),
                }
                for item in items
            ],
            "delivery_date": None,
            "notes": f"Commande démo - Call ID: {call_id}",
            "source": "agent_ia_demo",
            "external_order_id": call_id,
        }

        # Créer dans le mock ERP
        erp_response = await self.mock_erp.create_order(erp_data)

        # Envoyer notifications
        notification_results = await self.notifier.send_order_notification(
            order_id=erp_response["order_id"],
            pharmacy_name=pharmacy_name,
            items=items,
            total_amount=total_amount,
            via_email=len(self.notification_emails) > 0,
            via_whatsapp=self.notification_whatsapp is not None,
            email_to=self.notification_emails,
            whatsapp_to=self.notification_whatsapp,
        )

        return {
            "success": True,
            "order_id": erp_response["order_id"],
            "total_amount": total_amount,
            "erp_response": erp_response,
            "notifications_sent": notification_results,
            "mode": "DEMO",
            "message": "✅ Commande créée en mode DÉMO (aucune connexion ERP réelle)",
        }

    async def get_all_demo_orders(self) -> List[Dict[str, Any]]:
        """Récupérer toutes les commandes démo."""
        return self.mock_erp.get_all_orders()

