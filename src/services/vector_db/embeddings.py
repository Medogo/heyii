

# ========================================
# src/services/vector_db/embeddings.py
# ========================================
"""Génération d'embeddings pour les produits."""
from typing import List
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """Générateur d'embeddings pour recherche sémantique."""

    def __init__(
            self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"
    ):
        """
        Initialiser le générateur.

        Args:
            model_name: Nom du modèle sentence-transformers
        """
        self.model = SentenceTransformer(f"sentence-transformers/{model_name}")
        self.vector_size = 768

    def generate_embedding(self, text: str) -> List[float]:
        """
        Générer un embedding.

        Args:
            text: Texte à embedder

        Returns:
            Vecteur d'embedding
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Générer des embeddings en batch.

        Args:
            texts: Liste de textes

        Returns:
            Liste d'embeddings
        """
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]

    def generate_product_text(self, product: dict) -> str:
        """
        Créer le texte à embedder pour un produit.

        Args:
            product: Dictionnaire produit

        Returns:
            Texte optimisé pour embedding
        """
        parts = [product["name"]]

        if product.get("category"):
            parts.append(product["category"])

        # Ajouter des synonymes courants si disponibles
        # Exemple: "Doliprane" -> ajouter "paracétamol"

        return " ".join(parts)


# Instance globale
embedding_generator = EmbeddingGenerator()
