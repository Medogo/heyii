"""Modèle Pharmacy."""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.data.database import Base


class Pharmacy(Base):
    """Modèle pour les pharmacies."""

    __tablename__ = "pharmacies"

    id: Mapped[int] = mapped_column(primary_key=True)
    pharmacy_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    phone_number: Mapped[str] = mapped_column(String(20), unique=True)
    address: Mapped[str | None] = mapped_column(String(500))
    city: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )