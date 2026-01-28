"""Repository pour les appels."""
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data.models.call import Call
from src.data.repositories.base import BaseRepository


class CallRepository(BaseRepository[Call]):
    """Repository pour les appels téléphoniques."""

    def __init__(self, session: AsyncSession):
        super().__init__(Call, session)

    async def get_by_call_id(self, call_id: str, load_pharmacy: bool = False) -> Call | None:
        """Récupérer par call_id."""
        query = select(Call).where(Call.call_id == call_id)

        if load_pharmacy:
            query = query.options(selectinload(Call.pharmacy))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_pharmacy(self, pharmacy_id: int) -> list[Call]:
        """Récupérer tous les appels d'une pharmacie."""
        result = await self.session.execute(
            select(Call)
            .where(Call.pharmacy_id == pharmacy_id)
            .order_by(Call.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[Call]:
        """Récupérer tous les appels par statut."""
        result = await self.session.execute(
            select(Call)
            .where(Call.status == status)
            .order_by(Call.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_calls(self) -> list[Call]:
        """Récupérer tous les appels actifs (ringing ou active)."""
        result = await self.session.execute(
            select(Call)
            .where(Call.status.in_(["ringing", "active"]))
            .order_by(Call.started_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(self, call_id: int, status: str) -> Call | None:
        """Mettre à jour le statut."""
        call = await self.get_by_id(call_id)
        if not call:
            return None

        call.status = status

        if status in ["completed", "failed"]:
            call.ended_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(call)
        return call

    async def end_call(
            self, call_id: int, duration_seconds: int, confidence_global: float | None = None
    ) -> Call | None:
        """Terminer un appel."""
        call = await self.get_by_id(call_id)
        if not call:
            return None

        call.status = "completed"
        call.ended_at = datetime.utcnow()
        call.duration_seconds = duration_seconds

        if confidence_global is not None:
            call.confidence_global = confidence_global

        await self.session.commit()
        await self.session.refresh(call)
        return call