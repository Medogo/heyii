"""Repository de base."""
from typing import Generic, TypeVar, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository de base avec opérations CRUD."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        """Récupérer par ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Récupérer tous les enregistrements."""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: dict) -> ModelType:
        """Créer un enregistrement depuis un dict."""
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()  # ✅ Commit au lieu de flush
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, data: dict) -> ModelType | None:
        """Mettre à jour depuis un dict."""
        obj = await self.get_by_id(id)
        if not obj:
            return None

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        """Supprimer."""
        obj = await self.get_by_id(id)
        if not obj:
            return False

        await self.session.delete(obj)
        await self.session.commit()  # ✅ Commit au lieu de flush
        return True