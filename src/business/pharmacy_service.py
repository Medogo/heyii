"""Service métier pour la gestion des pharmacies."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.pharmacy_repository import PharmacyRepository
from src.data.models import Pharmacy


class PharmacyService:
    """Service de gestion des pharmacies."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PharmacyRepository(db)

    async def get_by_phone(self, phone_number: str) -> Optional[Pharmacy]:
        """Récupérer une pharmacie par numéro de téléphone."""
        return await self.repository.get_by_phone(phone_number)

    async def get_by_pharmacy_id(self, pharmacy_id: str) -> Optional[Pharmacy]:
        """Récupérer une pharmacie par ID métier."""
        return await self.repository.get_by_pharmacy_id(pharmacy_id)

    async def authenticate_caller(self, phone_number: str) -> Optional[Pharmacy]:
        """Authentifier un appelant par son numéro."""
        pharmacy = await self.get_by_phone(phone_number)

        if not pharmacy:
            print(f"⚠️  Pharmacie non reconnue: {phone_number}")
            return None

        if not pharmacy.is_active:
            print(f"⚠️  Pharmacie inactive: {pharmacy.name}")
            return None

        print(f"✅ Pharmacie authentifiée: {pharmacy.name} ({pharmacy.pharmacy_id})")

        return pharmacy