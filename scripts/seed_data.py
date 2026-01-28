"""Scripts utilitaires pour HEYI."""

# ========================================
# scripts/seed_data.py
# ========================================
"""Script pour peupler la base avec des données de test."""
import asyncio
import sys
from pathlib import Path

# Ajouter le projet au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.data.database import Base
from src.data.models.pharmacy import Pharmacy
from src.data.models.product import Product


async def create_tables(engine):
    """Créer toutes les tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables créées")


async def seed_pharmacies(session: AsyncSession):
    """Peupler les pharmacies."""
    pharmacies = [
        Pharmacy(
            pharmacy_id="pharma_0001",
            name="Pharmacie Centrale Cotonou",
            phone_number="+22900000001",
            address="Boulevard de la Marina",
            city="Cotonou",
            is_active=True,
        ),
        Pharmacy(
            pharmacy_id="pharma_0002",
            name="Pharmacie du Marché",
            phone_number="+22900000002",
            address="Marché Dantokpa",
            city="Cotonou",
            is_active=True,
        ),
        Pharmacy(
            pharmacy_id="pharma_0003",
            name="Pharmacie Saint Michel",
            phone_number="+22900000003",
            address="Avenue Steinmetz",
            city="Cotonou",
            is_active=True,
        ),
        Pharmacy(
            pharmacy_id="pharma_0004",
            name="Pharmacie de la Paix",
            phone_number="+22900000004",
            address="Rue des Cheminots",
            city="Porto-Novo",
            is_active=True,
        ),
        Pharmacy(
            pharmacy_id="pharma_0005",
            name="Pharmacie Moderne",
            phone_number="+22900000005",
            address="Quartier Zongo",
            city="Parakou",
            is_active=True,
        ),
    ]

    for pharmacy in pharmacies:
        session.add(pharmacy)

    await session.commit()
    print(f"✅ {len(pharmacies)} pharmacies créées")


async def seed_products(session: AsyncSession):
    """Peupler les produits."""
    products = [
        # Antalgiques
        Product(
            cip13="3400934823432",
            ean="3400934823432",
            name="DOLIPRANE 1000MG CPR SEC 8",
            category="Antalgique",
            supplier_code="DOL-1000-SEC",
            unit_price=5.50,
            stock_available=2000,
            stock_reserved=0,
        ),
        Product(
            cip13="3400935467891",
            ean="3400935467891",
            name="EFFERALGAN 1G CPR EFF 8",
            category="Antalgique",
            supplier_code="EFF-1G-8",
            unit_price=4.80,
            stock_available=1500,
            stock_reserved=0,
        ),
        Product(
            cip13="3400936789012",
            ean="3400936789012",
            name="DAFALGAN 1000MG CPR 16",
            category="Antalgique",
            supplier_code="DAF-1000-16",
            unit_price=6.20,
            stock_available=1000,
            stock_reserved=0,
        ),
        # Antispasmodiques
        Product(
            cip13="3400892567123",
            ean="3400892567123",
            name="SPASFON LYOC 80MG",
            category="Antispasmodique",
            supplier_code="SPA-LYOC-80",
            unit_price=8.20,
            stock_available=500,
            stock_reserved=0,
        ),
        Product(
            cip13="3400893456789",
            ean="3400893456789",
            name="SPASFON 80MG CPR ENROBE 30",
            category="Antispasmodique",
            supplier_code="SPA-80-30",
            unit_price=7.50,
            stock_available=800,
            stock_reserved=0,
        ),
        # Anti-inflammatoires
        Product(
            cip13="3400894567890",
            ean="3400894567890",
            name="IBUPROFENE 400MG CPR 30",
            category="Anti-inflammatoire",
            supplier_code="IBU-400-30",
            unit_price=3.90,
            stock_available=1200,
            stock_reserved=0,
        ),
        Product(
            cip13="3400895678901",
            ean="3400895678901",
            name="ADVIL 400MG CPR ENROBE 20",
            category="Anti-inflammatoire",
            supplier_code="ADV-400-20",
            unit_price=5.20,
            stock_available=900,
            stock_reserved=0,
        ),
        # Antibiotiques
        Product(
            cip13="3400896789012",
            ean="3400896789012",
            name="AMOXICILLINE 1G CPR 12",
            category="Antibiotique",
            supplier_code="AMX-1G-12",
            unit_price=9.80,
            stock_available=600,
            stock_reserved=0,
        ),
        Product(
            cip13="3400897890123",
            ean="3400897890123",
            name="AUGMENTIN 1G/125MG CPR 16",
            category="Antibiotique",
            supplier_code="AUG-1G-16",
            unit_price=12.50,
            stock_available=400,
            stock_reserved=0,
        ),
        # Vitamines
        Product(
            cip13="3400898901234",
            ean="3400898901234",
            name="VITAMINE C 500MG CPR EFF 20",
            category="Vitamine",
            supplier_code="VIT-C-500",
            unit_price=4.20,
            stock_available=1500,
            stock_reserved=0,
        ),
        Product(
            cip13="3400899012345",
            ean="3400899012345",
            name="MAGNESIUM B6 CPR 60",
            category="Vitamine",
            supplier_code="MAG-B6-60",
            unit_price=8.90,
            stock_available=700,
            stock_reserved=0,
        ),
        # Antihistaminiques
        Product(
            cip13="3400900123456",
            ean="3400900123456",
            name="CETIRIZINE 10MG CPR 15",
            category="Antihistaminique",
            supplier_code="CET-10-15",
            unit_price=6.50,
            stock_available=500,
            stock_reserved=0,
        ),
        # Antitussifs
        Product(
            cip13="3400901234567",
            ean="3400901234567",
            name="TOPLEXIL SIROP 150ML",
            category="Antitussif",
            supplier_code="TOP-SIR-150",
            unit_price=7.80,
            stock_available=300,
            stock_reserved=0,
        ),
        # Digestifs
        Product(
            cip13="3400902345678",
            ean="3400902345678",
            name="GAVISCON MENTHE SACHET 24",
            category="Digestif",
            supplier_code="GAV-MEN-24",
            unit_price=9.20,
            stock_available=450,
            stock_reserved=0,
        ),
        Product(
            cip13="3400903456789",
            ean="3400903456789",
            name="SMECTA VANILLE SACHET 18",
            category="Digestif",
            supplier_code="SME-VAN-18",
            unit_price=5.60,
            stock_available=800,
            stock_reserved=0,
        ),
    ]

    for product in products:
        session.add(product)

    await session.commit()
    print(f"✅ {len(products)} produits créés")


async def main():
    """Main function."""
    print("🚀 Seed Data - Début")

    # Créer l'engine
    engine = create_async_engine(settings.database_url, echo=False)

    # Créer les tables
    await create_tables(engine)

    # Créer une session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Peupler
        await seed_pharmacies(session)
        await seed_products(session)

    await engine.dispose()

    print("✅ Seed Data - Terminé")


if __name__ == "__main__":
    asyncio.run(main())



