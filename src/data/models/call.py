"""Modèle Call."""
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.database import Base


class Call(Base):
    """Modèle pour les appels téléphoniques."""

    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    pharmacy_id: Mapped[int] = mapped_column(ForeignKey("pharmacies.id"))
    phone_number: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(50))  # ringing, active, completed, failed
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    confidence_global: Mapped[float | None] = mapped_column(Float)
    audio_recording_url: Mapped[str | None] = mapped_column(String(500))
    agent_version: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relation
    pharmacy: Mapped["Pharmacy"] = relationship("Pharmacy")