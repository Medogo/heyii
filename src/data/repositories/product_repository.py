"""Repository pour les produits."""
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.product import Product
from src.data.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository pour les produits."""

    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_by_cip13(self, cip13: str) -> Product | None:
        """Récupérer par code CIP13."""
        result = await self.session.execute(
            select(Product).where(Product.cip13 == cip13)
        )
        return result.scalar_one_or_none()

    async def get_by_ean(self, ean: str) -> Product | None:
        """Récupérer par EAN."""
        result = await self.session.execute(
            select(Product).where(Product.ean == ean)
        )
        return result.scalar_one_or_none()

    async def search_by_name(self, name: str, limit: int = 10) -> list[Product]:
        """Rechercher par nom (LIKE)."""
        result = await self.session.execute(
            select(Product)
            .where(Product.name.ilike(f"%{name}%"))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search(self, query: str, limit: int = 10) -> list[Product]:
        """Recherche par nom ou CIP."""
        result = await self.session.execute(
            select(Product)
            .where(
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.cip13.like(f"%{query}%"),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> list[Product]:
        """Récupérer tous les produits d'une catégorie."""
        result = await self.session.execute(
            select(Product).where(Product.category == category)
        )
        return list(result.scalars().all())

    async def update_stock(
        self, product_id: int, available: int | None = None, reserved: int | None = None
    ) -> Product | None:
        """Mettre à jour le stock."""
        product = await self.get_by_id(product_id)
        if not product:
            return None

        if available is not None:
            product.stock_available = available
        if reserved is not None:
            product.stock_reserved = reserved

        await self.session.commit()
        await self.session.refresh(product)
        return product