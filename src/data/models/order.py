"""Modèle Order."""
from datetime import datetime, date
from sqlalchemy import String, Float, Integer, DateTime, Date, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.database import Base


class Order(Base):
    """Modèle pour les commandes."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"))
    pharmacy_id: Mapped[int] = mapped_column(ForeignKey("pharmacies.id"))

    status: Mapped[str] = mapped_column(String(50))  # pending, confirmed, cancelled
    total_amount: Mapped[float] = mapped_column(Float)

    delivery_date: Mapped[date | None] = mapped_column(Date)
    delivery_notes: Mapped[str | None] = mapped_column(Text)

    required_human_review: Mapped[bool] = mapped_column(Boolean, default=False)
    review_reason: Mapped[str | None] = mapped_column(String(200))

    erp_created: Mapped[bool] = mapped_column(Boolean, default=False)
    erp_order_id: Mapped[str | None] = mapped_column(String(100))

    validated_by_human: Mapped[str | None] = mapped_column(String(100))
    validated_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    call: Mapped["Call"] = relationship("Call")
    pharmacy: Mapped["Pharmacy"] = relationship("Pharmacy")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """Modèle pour les lignes de commande."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    audio_transcript: Mapped[str | None] = mapped_column(Text)
    quantity_asked: Mapped[int] = mapped_column(Integer)
    quantity_unit: Mapped[str] = mapped_column(String(20))  # boites, unités

    unit_price: Mapped[float] = mapped_column(Float)
    line_total: Mapped[float] = mapped_column(Float)

    confidence_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50))  # ok, out_of_stock, unavailable

    extracted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")