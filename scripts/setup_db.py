
# ========================================
# scripts/setup_db.py
# ========================================
"""Script pour setup initial de la base."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings
from src.data.database import Base


async def setup_database():
    """Setup la base de données."""
    print("🔧 Setup de la base de données")

    engine = create_async_engine(settings.database_url, echo=True)

    async with engine.begin() as conn:
        # Créer toutes les tables
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

    print("✅ Base de données créée")


if __name__ == "__main__":
    asyncio.run(setup_database())