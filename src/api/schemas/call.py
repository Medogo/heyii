"""Schémas Pydantic pour les appels."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CallBase(BaseModel):
    """Schéma de base pour un appel."""
    phone_number: str = Field(..., description="Numéro de téléphone")


class CallCreate(CallBase):
    """Schéma pour créer un appel."""
    pass


class CallResponse(CallBase):
    """Schéma de réponse pour un appel."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    call_id: str
    status: str
    duration_seconds: Optional[int] = None
    confidence_global: Optional[float] = None
    audio_recording_url: Optional[str] = None
    agent_version: str
    started_at: datetime
    ended_at: Optional[datetime] = None


class CallStats(BaseModel):
    """Statistiques des appels."""
    total_calls: int
    active_calls: int
    completed_calls: int
    failed_calls: int
    average_duration: float
    average_confidence: float