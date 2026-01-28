"""Routes pour la gestion des commandes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import get_db
from src.data.repositories.order_repository import OrderRepository
from src.api.schemas.order import OrderResponse, OrderCreate, OrderStats

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
        skip: int = 0,
        limit: int = 100,
        status: str | None = Query(None, description="Filter by status"),
        db: AsyncSession = Depends(get_db)
):
    """Lister toutes les commandes."""
    repo = OrderRepository(db)

    if status:
        orders = await repo.get_by_status(status, skip=skip, limit=limit)
    else:
        orders = await repo.get_all(skip=skip, limit=limit)

    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
        order_id: str,
        db: AsyncSession = Depends(get_db)
):
    """Récupérer une commande par ID."""
    repo = OrderRepository(db)
    order = await repo.get_by_order_id(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.post("/", response_model=OrderResponse)
async def create_order(
        order_data: OrderCreate,
        db: AsyncSession = Depends(get_db)
):
    """Créer une nouvelle commande manuellement."""
    # Cette route serait normalement utilisée par l'orchestrateur
    # mais peut servir pour tests ou backup manuel

    from src.business.order_service import OrderService

    order_service = OrderService(db)

    try:
        order = await order_service.create_order_from_api(order_data)
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/validate")
async def validate_order(
        order_id: str,
        validated_by: str,
        db: AsyncSession = Depends(get_db)
):
    """Valider une commande manuellement."""
    repo = OrderRepository(db)
    order = await repo.get_by_order_id(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.validated_by_human = validated_by
    order.validated_at = datetime.utcnow()
    order.required_human_review = False

    await repo.update(order)

    return {"message": f"Order {order_id} validated by {validated_by}"}


@router.get("/stats/summary", response_model=OrderStats)
async def get_order_stats(db: AsyncSession = Depends(get_db)):
    """Statistiques des commandes."""
    repo = OrderRepository(db)
    stats = await repo.get_stats()
    return stats


@router.get("/pending/review", response_model=List[OrderResponse])
async def get_pending_review_orders(
        limit: int = 50,
        db: AsyncSession = Depends(get_db)
):
    """Récupérer les commandes en attente de validation."""
    repo = OrderRepository(db)
    orders = await repo.get_pending_review(limit=limit)
    return orders