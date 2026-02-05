"""Repository pour les commandes."""
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data.models.order import Order, OrderItem
from src.data.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Repository pour les commandes."""

    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_order_id(
            self, order_id: str, load_relations: bool = False
    ) -> Order | None:
        """Récupérer par order_id."""
        query = select(Order).where(Order.order_id == order_id)

        if load_relations:
            query = query.options(
                selectinload(Order.call),
                selectinload(Order.pharmacy),
                selectinload(Order.items).selectinload(OrderItem.product),
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_call(self, call_id: int) -> Order | None:
        """Récupérer par call_id."""
        result = await self.session.execute(
            select(Order)
            .where(Order.call_id == call_id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        return result.scalar_one_or_none()

    async def get_by_pharmacy(self, pharmacy_id: int) -> list[Order]:
        """Récupérer toutes les commandes d'une pharmacie."""
        result = await self.session.execute(
            select(Order)
            .where(Order.pharmacy_id == pharmacy_id)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[Order]:
        """Récupérer par statut."""
        result = await self.session.execute(
            select(Order)
            .where(Order.status == status)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_review(self) -> list[Order]:
        """Récupérer les commandes nécessitant une revue humaine."""
        result = await self.session.execute(
            select(Order)
            .where(Order.required_human_review == True)
            .where(Order.validated_by_human.is_(None))
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(self, order_id: int, status: str) -> Order | None:
        """Mettre à jour le statut."""
        order = await self.get_by_id(order_id)
        if not order:
            return None

        order.status = status
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def validate_by_human(
            self, order_id: int, validated_by: str
    ) -> Order | None:
        """Valider par un humain."""
        order = await self.get_by_id(order_id)
        if not order:
            return None

        order.validated_by_human = validated_by
        order.validated_at = datetime.utcnow()
        order.required_human_review = False

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def mark_erp_created(
            self, order_id: int, erp_order_id: str
    ) -> Order | None:
        """Marquer comme créée dans l'ERP."""
        order = await self.get_by_id(order_id)
        if not order:
            return None

        order.erp_created = True
        order.erp_order_id = erp_order_id

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_stats(self):
        """Calculer les statistiques des commandes."""
        # Total des commandes
        total_result = await self.session.execute(select(func.count(Order.id)))
        total_orders = total_result.scalar() or 0

        # Commandes en attente
        pending_result = await self.session.execute(
            select(func.count(Order.id)).where(Order.status == "pending")
        )
        pending_orders = pending_result.scalar() or 0

        # Commandes complétées
        completed_result = await self.session.execute(
            select(func.count(Order.id)).where(Order.status == "confirmed")
        )
        completed_orders = completed_result.scalar() or 0

        # Montant total
        total_amount_result = await self.session.execute(
            select(func.sum(Order.total_amount))
        )
        total_amount = total_amount_result.scalar() or 0.0
        if total_amount:
            total_amount = float(total_amount)

        # Nombre moyen d'items par commande
        # On compte le nombre total d'items et on divise par le nombre de commandes
        items_count_result = await self.session.execute(
            select(func.count(OrderItem.id))
        )
        total_items = items_count_result.scalar() or 0
        average_items_per_order = (
            float(total_items) / total_orders if total_orders > 0 else 0.0
        )

        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "total_amount": total_amount,
            "average_items_per_order": average_items_per_order,
        }


class OrderItemRepository(BaseRepository[OrderItem]):
    """Repository pour les lignes de commande."""

    def __init__(self, session: AsyncSession):
        super().__init__(OrderItem, session)

    async def create_many(self, items_data: list[dict]) -> list[OrderItem]:
        """Créer plusieurs lignes de commande."""
        items = [OrderItem(**data) for data in items_data]
        self.session.add_all(items)
        await self.session.commit()

        for item in items:
            await self.session.refresh(item)

        return items

    async def get_by_order(self, order_id: int) -> list[OrderItem]:
        """Récupérer toutes les lignes d'une commande."""
        result = await self.session.execute(
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
            .options(selectinload(OrderItem.product))
        )
        return list(result.scalars().all())