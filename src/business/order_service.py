"""Service métier pour la gestion des commandes."""
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.order_repository import OrderRepository
from src.data.repositories.product_repository import ProductRepository
from src.data.models import Order, OrderItem
from src.business.product_service import ProductService
from src.integrations.erp.client import ERPClient


class OrderService:
    """Service de gestion des commandes."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderRepository(db)
        self.product_service = ProductService(db)
        self.erp_client = ERPClient()

    async def create_order(
            self,
            call_id: str,
            pharmacy_id: str,
            items: List[Dict[str, Any]],
            confidence: float,
            delivery_notes: Optional[str] = None,
    ) -> Order:
        """Créer une nouvelle commande."""

        # Générer l'ID de commande
        order_id = self._generate_order_id()

        # Calculer le total et vérifier les stocks
        total_amount = 0.0
        order_items_data = []

        for item_data in items:
            product_cip = item_data["product_cip"]
            quantity = item_data["quantity"]

            # Récupérer le produit
            product = await self.product_service.get_by_cip(product_cip)
            if not product:
                raise ValueError(f"Product not found: {product_cip}")

            # Vérifier le stock
            stock_ok = await self.product_service.check_stock(product_cip, quantity)

            # Calculer le total
            line_total = product.unit_price * quantity
            total_amount += line_total

            order_items_data.append({
                "product_id": product.id,
                "product_cip": product_cip,
                "product_name": product.name,
                "quantity": quantity,
                "unit": item_data.get("unit", "boites"),
                "unit_price": product.unit_price,
                "line_total": line_total,
                "audio_transcript": item_data.get("transcript"),
                "confidence_score": item_data.get("confidence"),
                "status": "ok" if stock_ok else "out_of_stock",
            })

        # Déterminer si validation humaine requise
        requires_review = self._requires_human_review(
            total_amount=total_amount,
            confidence=confidence,
            items=order_items_data
        )

        # Créer la commande en base
        order = Order(
            order_id=order_id,
            call_id=call_id,
            pharmacy_id=pharmacy_id,
            status="pending" if requires_review else "confirmed",
            total_amount=total_amount,
            delivery_notes=delivery_notes,
            required_human_review=requires_review,
            review_reason=self._get_review_reason(total_amount, confidence),
            confidence_global=confidence,
            erp_created=False,
        )

        created_order = await self.repository.create(order)

        # Créer les lignes de commande
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=created_order.id,
                product_id=item_data["product_id"],
                audio_transcript=item_data["audio_transcript"],
                quantity_asked=item_data["quantity"],
                quantity_unit=item_data["unit"],
                unit_price=item_data["unit_price"],
                line_total=item_data["line_total"],
                confidence_score=item_data["confidence_score"],
                status=item_data["status"],
            )
            self.db.add(order_item)

        await self.db.commit()
        await self.db.refresh(created_order)

        print(f"✅ Commande créée: {order_id} (Total: {total_amount:.2f}€)")

        # Si pas besoin de review, envoyer à l'ERP
        if not requires_review:
            try:
                await self.send_to_erp(created_order)
            except Exception as e:
                print(f"❌ Erreur envoi ERP: {e}")
                # La commande est créée mais pas dans l'ERP

        return created_order

    async def send_to_erp(self, order: Order) -> str:
        """Envoyer une commande à l'ERP."""

        # Récupérer les items
        await self.db.refresh(order, ["items"])

        # Préparer les données pour l'ERP
        erp_payload = {
            "pharmacy_id": order.pharmacy_id,
            "order_date": order.created_at.isoformat(),
            "items": [
                {
                    "product_cip13": item.product.cip13,
                    "quantity": item.quantity_asked,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                }
                for item in order.items
            ],
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
            "notes": order.delivery_notes,
            "source": "agent_ia_v1",
            "external_order_id": order.order_id,
        }

        # Envoyer à l'ERP
        erp_response = await self.erp_client.create_order(erp_payload)

        # Mettre à jour la commande
        order.erp_created = True
        order.erp_order_id = erp_response["order_id"]
        order.status = "confirmed"

        await self.repository.update(order)

        # Réserver les stocks
        for item in order.items:
            await self.product_service.reserve_stock(
                item.product.cip13,
                item.quantity_asked
            )

        print(f"✅ Commande envoyée à l'ERP: {erp_response['order_id']}")

        return erp_response["order_id"]

    def _generate_order_id(self) -> str:
        """Générer un ID de commande unique."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"CMD-{timestamp}"

    def _requires_human_review(
            self,
            total_amount: float,
            confidence: float,
            items: List[Dict[str, Any]]
    ) -> bool:
        """Déterminer si la commande nécessite une validation humaine."""

        # Seuil montant
        if total_amount > 10000:
            return True

        # Confiance trop basse
        if confidence < 0.85:
            return True

        # Produits en rupture
        if any(item["status"] == "out_of_stock" for item in items):
            return True

        return False

    def _get_review_reason(
            self,
            total_amount: float,
            confidence: float
    ) -> Optional[str]:
        """Obtenir la raison de la review."""

        reasons = []

        if total_amount > 10000:
            reasons.append(f"Montant élevé: {total_amount:.2f}€")

        if confidence < 0.85:
            reasons.append(f"Confiance basse: {confidence:.2f}")

        return " | ".join(reasons) if reasons else None

    async def validate_order(
            self,
            order_id: str,
            validated_by: str
    ) -> Order:
        """Valider manuellement une commande."""

        order = await self.repository.get_by_order_id(order_id)
        if not order:
            raise ValueError(f"Order not found: {order_id}")

        order.validated_by_human = validated_by
        order.validated_at = datetime.utcnow()
        order.required_human_review = False

        await self.repository.update(order)

        # Envoyer à l'ERP si pas encore fait
        if not order.erp_created:
            await self.send_to_erp(order)

        print(f"✅ Commande validée par {validated_by}: {order_id}")

        return order