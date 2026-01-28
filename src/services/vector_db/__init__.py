"""Service base de données vectorielle."""
from src.services.vector_db.qcadrant_client import qdrant_client, QdrantClient
from src.services.vector_db.embeddings import EmbeddingGenerator, embedding_generator
from src.services.vector_db.indexer import ProductIndexer, product_indexer

__all__ = [
    "qdrant_client",
    "QdrantClient",
    "EmbeddingGenerator",
    "embedding_generator",
    "ProductIndexer",
    "product_indexer",
]
