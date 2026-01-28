"""Modèle Product."""
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.data.database import Base


class Product(Base):
    """Modèle pour les produits pharmaceutiques."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    cip13: Mapped[str] = mapped_column(String(13), unique=True, index=True)
    ean: Mapped[str] = mapped_column(String(13))
    name: Mapped[str] = mapped_column(String(500), index=True)
    category: Mapped[str | None] = mapped_column(String(100))
    supplier_code: Mapped[str | None] = mapped_column(String(50))
    unit_price: Mapped[float] = mapped_column(Float)
    stock_available: Mapped[int] = mapped_column(Integer, default=0)
    stock_reserved: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )