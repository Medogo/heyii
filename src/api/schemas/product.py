"""Schémas Pydantic pour les produits."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    """Schéma de base pour un produit."""
    cip13: str = Field(..., min_length=13, max_length=13)
    name: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = None
    unit_price: float = Field(..., gt=0)


class ProductCreate(ProductBase):
    """Schéma pour créer un produit."""
    ean: str
    supplier_code: Optional[str] = None
    stock_available: int = Field(default=0, ge=0)


class ProductResponse(ProductBase):
    """Schéma de réponse pour un produit."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ean: str
    supplier_code: Optional[str] = None
    stock_available: int
    stock_reserved: int
    created_at: datetime
    updated_at: datetime


class ProductSearch(BaseModel):
    """Résultat de recherche de produit."""
    product: ProductResponse
    score: float = Field(..., ge=0, le=1, description="Score de pertinence")
    match_type: str = Field(..., description="Type de match (exact, fuzzy, semantic)")


class StockCheckRequest(BaseModel):
    """Requête de vérification de stock."""
    cip13: str
    quantity: int = Field(..., gt=0)


class StockCheckResponse(BaseModel):
    """Réponse de vérification de stock."""
    cip13: str
    requested: int
    available: int
    is_available: bool