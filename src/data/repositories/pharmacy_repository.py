"""Repository pour les pharmacies."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.pharmacy import Pharmacy
from src.data.repositories.base import BaseRepository


class PharmacyRepository(BaseRepository[Pharmacy]):
    """Repository pour les pharmacies."""

    def __init__(self, session: AsyncSession):
        super().__init__(Pharmacy, session)

    async def get_by_pharmacy_id(self, pharmacy_id: str) -> Pharmacy | None:
        """Récupérer par pharmacy_id."""
        result = await self.session.execute(
            select(Pharmacy).where(Pharmacy.pharmacy_id == pharmacy_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone_number: str) -> Pharmacy | None:
        """Récupérer par numéro de téléphone."""
        result = await self.session.execute(
            select(Pharmacy).where(Pharmacy.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Pharmacy]:
        """Récupérer toutes les pharmacies actives."""
        result = await self.session.execute(
            select(Pharmacy).where(Pharmacy.is_active == True)
        )
        return list(result.scalars().all())

    async def get_by_city(self, city: str) -> list[Pharmacy]:
        """Récupérer toutes les pharmacies d'une ville."""
        result = await self.session.execute(
            select(Pharmacy).where(Pharmacy.city == city)
        )
        return list(result.scalars().all())

    async def deactivate(self, pharmacy_id: int) -> Pharmacy | None:
        """Désactiver une pharmacie."""
        pharmacy = await self.get_by_id(pharmacy_id)
        if not pharmacy:
            return None

        pharmacy.is_active = False
        await self.session.commit()
        await self.session.refresh(pharmacy)
        return pharmacy

    async def activate(self, pharmacy_id: int) -> Pharmacy | None:
        """Activer une pharmacie."""
        pharmacy = await self.get_by_id(pharmacy_id)
        if not pharmacy:
            return None

        pharmacy.is_active = True
        await self.session.commit()
        await self.session.refresh(pharmacy)
        return pharmacy