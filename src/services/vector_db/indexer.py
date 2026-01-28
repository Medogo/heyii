
# ========================================
# src/services/vector_db/indexer.py
# ========================================
"""Indexeur de produits pour Qdrant."""
import asyncio
from typing import List, Dict, Any

from src.services.vector_db.embeddings import embedding_generator
from src.services.vector_db.qcadrant_client import qdrant_client


class ProductIndexer:
    """Indexeur de produits dans Qdrant."""

    def __init__(self):
        """Initialiser l'indexeur."""
        self.batch_size = 50

    async def index_products(self, products: List[Dict[str, Any]]) -> int:
        """
        Indexer une liste de produits.

        Args:
            products: Liste de produits

        Returns:
            Nombre de produits indexés
        """
        total_indexed = 0

        # Indexer par batch
        for i in range(0, len(products), self.batch_size):
            batch = products[i: i + self.batch_size]

            count = await qdrant_client.index_products_batch(batch)
            total_indexed += count

            print(f"📦 Batch {i // self.batch_size + 1}: {count} produits indexés")

        return total_indexed

    async def reindex_all(self, products: List[Dict[str, Any]]) -> int:
        """
        Réindexer tous les produits (efface et recréé).

        Args:
            products: Liste de produits

        Returns:
            Nombre indexé
        """
        print("🔄 Réindexation complète...")

        # Réinitialiser la collection
        await qdrant_client.initialize_collection()

        # Indexer
        return await self.index_products(products)


# Instance globale
product_indexer = ProductIndexer()