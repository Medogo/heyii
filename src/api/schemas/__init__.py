"""Schémas Pydantic pour l'API."""
from src.api.schemas.call import CallBase, CallCreate, CallResponse, CallStats
from src.api.schemas.order import (
    OrderItemBase,
    OrderItemCreate,
    OrderItemResponse,
    OrderBase,
    OrderCreate,
    OrderResponse,
    OrderStats,
)
from src.api.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductResponse,
    ProductSearch,
    StockCheckRequest,
    StockCheckResponse,
)

__all__ = [
    # Call schemas
    "CallBase",
    "CallCreate",
    "CallResponse",
    "CallStats",
    # Order schemas
    "OrderItemBase",
    "OrderItemCreate",
    "OrderItemResponse",
    "OrderBase",
    "OrderCreate",
    "OrderResponse",
    "OrderStats",
    # Product schemas
    "ProductBase",
    "ProductCreate",
    "ProductResponse",
    "ProductSearch",
    "StockCheckRequest",
    "StockCheckResponse",
]
