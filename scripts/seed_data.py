"""Script pour peupler la base avec des données de test."""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import engine, AsyncSessionLocal, Base
from src.data.models import Pharmacy, Product


async def seed_database():
    """Peupler la base de données."""

    # Créer les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Pharmacies
        pharmacies = [
            Pharmacy(
                pharmacy_id="pharma_0001",
                name="Pharmacie Centrale Cotonou",
                phone_number="+22900000001",
                address="Boulevard de la Marina",
                city="Cotonou",
            ),
            Pharmacy(
                pharmacy_id="pharma_0002",
                name="Pharmacie du Marché",
                phone_number="+22900000002",
                address="Marché Dantokpa",
                city="Cotonou",
            ),
        ]
        session.add_all(pharmacies)

        # Produits
        products = [
            Product(
                cip13="3400934823432",
                ean="3400934823432",
                name="DOLIPRANE 1000MG CPR SEC 8",
                category="Antalgique",
                supplier_code="DOL-1000-SEC",
                unit_price=5.50,
                stock_available=2000,
            ),
            Product(
                cip13="3400892567123",
                ean="3400892567123",
                name="SPASFON LYOC 80MG",
                category="Antispasmodique",
                supplier_code="SPA-LYOC-80",
                unit_price=8.20,
                stock_available=500,
            ),
            Product(
                cip13="3400935467891",
                ean="3400935467891",
                name="EFFERALGAN 1G CPR EFF 8",
                category="Antalgique",
                supplier_code="EFF-1G-8",
                unit_price=4.80,
                stock_available=1500,
            ),
        ]
        session.add_all(products)

        await session.commit()
        print("✅ Base de données peuplée avec succès!")


if __name__ == "__main__":
    asyncio.run(seed_database())