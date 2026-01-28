"""Service métier pour la gestion des produits."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.product_repository import ProductRepository
from src.data.models import Product
from src.utils.cache import cache


class ProductService:
    """Service de gestion des produits."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ProductRepository(db)

    async def get_by_cip(self, cip13: str, use_cache: bool = True) -> Optional[Product]:
        """Récupérer un produit par CIP avec cache."""

        # Vérifier le cache d'abord
        if use_cache:
            cache_key = f"product:cip:{cip13}"
            cached = await cache.get(cache_key)

            if cached:
                print(f"✅ Cache HIT: {cip13}")
                # Reconstruire l'objet Product depuis le cache
                return Product(**cached)

        # Récupérer depuis la base
        product = await self.repository.get_by_cip(cip13)

        if product and use_cache:
            # Mettre en cache
            cache_key = f"product:cip:{cip13}"
            product_dict = {
                "id": product.id,
                "cip13": product.cip13,
                "ean": product.ean,
                "name": product.name,
                "category": product.category,
                "supplier_code": product.supplier_code,
                "unit_price": product.unit_price,
                "stock_available": product.stock_available,
                "stock_reserved": product.stock_reserved,
            }
            await cache.set(cache_key, product_dict, ttl=300)  # 5 minutes

        return product

    async def search_products(
            self,
            query: str,
            limit: int = 10
    ) -> List[Product]:
        """Rechercher des produits."""
        return await self.repository.search(query, limit=limit)

    async def check_stock(
            self,
            cip13: str,
            quantity: int
    ) -> bool:
        """Vérifier si le stock est suffisant."""
        product = await self.get_by_cip(cip13)

        if not product:
            return False

        available = product.stock_available - product.stock_reserved
        return available >= quantity

    async def reserve_stock(
            self,
            cip13: str,
            quantity: int
    ) -> bool:
        """Réserver du stock pour une commande."""
        product = await self.get_by_cip(cip13, use_cache=False)

        if not product:
            raise ValueError(f"Product not found: {cip13}")

        available = product.stock_available - product.stock_reserved

        if available < quantity:
            raise ValueError(
                f"Insufficient stock for {product.name}: "
                f"requested {quantity}, available {available}"
            )

        # Réserver
        product.stock_reserved += quantity
        await self.repository.update(product)

        # Invalider le cache
        cache_key = f"product:cip:{cip13}"
        await cache.delete(cache_key)

        print(f"✅ Stock réservé: {quantity} x {product.name}")

        return True

    async def release_stock(
            self,
            cip13: str,
            quantity: int
    ) -> bool:
        """Libérer du stock réservé."""
        product = await self.get_by_cip(cip13, use_cache=False)

        if not product:
            return False

        product.stock_reserved = max(0, product.stock_reserved - quantity)
        await self.repository.update(product)

        # Invalider le cache
        cache_key = f"product:cip:{cip13}"
        await cache.delete(cache_key)

        return True

    async def update_stock_from_erp(
            self,
            cip13: str,
            new_stock: int
    ) -> Product:
        """Mettre à jour le stock depuis l'ERP."""
        product = await self.get_by_cip(cip13, use_cache=False)

        if not product:
            raise ValueError(f"Product not found: {cip13}")

        product.stock_available = new_stock
        await self.repository.update(product)

        # Invalider le cache
        cache_key = f"product:cip:{cip13}"
        await cache.delete(cache_key)

        print(f"📦 Stock mis à jour: {product.name} = {new_stock}")

        return product