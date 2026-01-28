"""Schémas Pydantic pour les commandes."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class OrderItemBase(BaseModel):
    """Schéma de base pour un item de commande."""
    product_cip: str = Field(..., description="Code CIP13 du produit")
    quantity: int = Field(..., gt=0, description="Quantité commandée")
    unit: str = Field(default="boites", description="Unité (boites, unités)")


class OrderItemCreate(OrderItemBase):
    """Schéma pour créer un item."""
    audio_transcript: Optional[str] = None
    confidence_score: Optional[float] = None


class OrderItemResponse(OrderItemBase):
    """Schéma de réponse pour un item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_name: str
    unit_price: float
    line_total: float
    status: str
    extracted_at: datetime


class OrderBase(BaseModel):
    """Schéma de base pour une commande."""
    pharmacy_id: int
    delivery_notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Schéma pour créer une commande."""
    call_id: str
    items: List[OrderItemCreate]


class OrderResponse(OrderBase):
    """Schéma de réponse pour une commande."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: str
    call_id: int
    status: str
    total_amount: float
    delivery_date: Optional[date] = None
    required_human_review: bool
    erp_created: bool
    erp_order_id: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse]


class OrderStats(BaseModel):
    """Statistiques des commandes."""
    total_orders: int
    pending_orders: int
    completed_orders: int
    total_amount: float
    average_items_per_order: float