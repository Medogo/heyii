
# ========================================
# scripts/index_products.py
# ========================================
"""Script pour indexer les produits dans Qdrant."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.data.repositories.product_repository import ProductRepository
from src.services.vector_db.qdrant_client import qdrant_client


async def index_all_products():
    """Indexer tous les produits dans Qdrant."""
    print("🚀 Indexation des produits dans Qdrant")

    # Connexion DB
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialiser Qdrant
    await qdrant_client.initialize_collection()

    async with async_session() as session:
        # Récupérer tous les produits
        repo = ProductRepository(session)
        products = await repo.get_all(skip=0, limit=1000)

        print(f"📦 {len(products)} produits à indexer")

        # Convertir en dict
        products_dict = [
            {
                "id": p.id,
                "cip13": p.cip13,
                "ean": p.ean,
                "name": p.name,
                "category": p.category,
                "supplier_code": p.supplier_code,
                "unit_price": p.unit_price,
            }
            for p in products
        ]

        # Indexer en batch
        indexed_count = await qdrant_client.index_products_batch(products_dict)

        print(f"✅ {indexed_count} produits indexés dans Qdrant")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(index_all_products())