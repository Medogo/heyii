"""Client Qdrant pour recherche vectorielle de produits."""
import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient as QdrantClientSDK
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from src.core.config import settings


class QdrantClient:
    """Client pour Qdrant Vector Database."""

    def __init__(self):
        """Initialiser le client Qdrant."""
        self.client = QdrantClientSDK(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
            timeout=5,
        )

        self.collection_name = settings.qdrant_collection

        # Modèle d'embeddings pour français
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        )

        # Dimension des embeddings
        self.vector_size = 768

    async def initialize_collection(self):
        """Créer la collection si elle n'existe pas."""
        try:
            # Vérifier si la collection existe
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                print(f"📦 Création collection Qdrant: {self.collection_name}")

                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size, distance=Distance.COSINE
                    ),
                )

                print(f"✅ Collection créée: {self.collection_name}")
            else:
                print(f"✅ Collection existe: {self.collection_name}")

        except Exception as e:
            print(f"❌ Erreur initialisation Qdrant: {e}")
            raise

    async def index_product(self, product: Dict[str, Any]) -> bool:
        """
        Indexer un produit dans Qdrant.

        Args:
            product: Dictionnaire avec infos produit

        Returns:
            True si succès
        """
        try:
            # Créer le texte à embedder (nom + catégorie + synonymes potentiels)
            text_to_embed = f"{product['name']} {product.get('category', '')}"

            # Générer l'embedding
            embedding = self.embedding_model.encode(text_to_embed).tolist()

            # Créer le point
            point = PointStruct(
                id=product["id"],
                vector=embedding,
                payload={
                    "cip13": product["cip13"],
                    "ean": product.get("ean"),
                    "name": product["name"],
                    "category": product.get("category"),
                    "supplier_code": product.get("supplier_code"),
                    "unit_price": product.get("unit_price"),
                },
            )

            # Insérer dans Qdrant
            self.client.upsert(
                collection_name=self.collection_name, points=[point], wait=True
            )

            print(f"✅ Produit indexé: {product['name']}")
            return True

        except Exception as e:
            print(f"❌ Erreur indexation produit: {e}")
            return False

    async def index_products_batch(self, products: List[Dict[str, Any]]) -> int:
        """
        Indexer plusieurs produits en batch.

        Args:
            products: Liste de produits

        Returns:
            Nombre de produits indexés
        """
        try:
            points = []

            for product in products:
                text_to_embed = f"{product['name']} {product.get('category', '')}"
                embedding = self.embedding_model.encode(text_to_embed).tolist()

                point = PointStruct(
                    id=product["id"],
                    vector=embedding,
                    payload={
                        "cip13": product["cip13"],
                        "ean": product.get("ean"),
                        "name": product["name"],
                        "category": product.get("category"),
                        "supplier_code": product.get("supplier_code"),
                        "unit_price": product.get("unit_price"),
                    },
                )
                points.append(point)

            # Insérer en batch
            self.client.upsert(
                collection_name=self.collection_name, points=points, wait=True
            )

            print(f"✅ {len(points)} produits indexés")
            return len(points)

        except Exception as e:
            print(f"❌ Erreur indexation batch: {e}")
            return 0

    async def search_product(
            self, query: str, limit: int = 5, score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Rechercher des produits par similarité sémantique.

        Args:
            query: Texte de recherche
            limit: Nombre max de résultats
            score_threshold: Seuil de score minimal

        Returns:
            Liste de résultats avec scores
        """
        try:
            # Générer l'embedding de la requête
            query_embedding = self.embedding_model.encode(query).tolist()

            # Rechercher dans Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Formater les résultats
            results = []
            for hit in search_result:
                results.append(
                    {
                        "product": hit.payload,
                        "score": hit.score,
                        "match_type": "semantic",
                    }
                )

            print(f"🔍 Recherche '{query}': {len(results)} résultats")

            return results

        except Exception as e:
            print(f"❌ Erreur recherche Qdrant: {e}")
            return []

    async def search_product_fuzzy(
            self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recherche floue avec phonétique (fallback si recherche sémantique échoue).

        Args:
            query: Texte de recherche
            limit: Nombre max de résultats

        Returns:
            Liste de résultats
        """
        try:
            # D'abord essayer recherche sémantique
            results = await self.search_product(query, limit=limit)

            if results:
                return results

            # Si pas de résultats, essayer recherche phonétique/fuzzy
            # (Implémentation simplifiée - pourrait être améliorée)
            query_lower = query.lower()

            # Rechercher tous les produits et filtrer par similarité de nom
            all_points = self.client.scroll(
                collection_name=self.collection_name, limit=100, with_payload=True
            )[0]

            fuzzy_matches = []
            for point in all_points:
                product_name = point.payload.get("name", "").lower()

                # Vérifier si le query est contenu dans le nom
                if query_lower in product_name or product_name in query_lower:
                    fuzzy_matches.append(
                        {
                            "product": point.payload,
                            "score": 0.7,  # Score arbitraire pour fuzzy
                            "match_type": "fuzzy",
                        }
                    )

            print(f"🔍 Recherche fuzzy '{query}': {len(fuzzy_matches)} résultats")

            return fuzzy_matches[:limit]

        except Exception as e:
            print(f"❌ Erreur recherche fuzzy: {e}")
            return []

    async def get_product_by_cip(self, cip13: str) -> Optional[Dict[str, Any]]:
        """
        Récupérer un produit par son code CIP.

        Args:
            cip13: Code CIP13

        Returns:
            Produit ou None
        """
        try:
            # Rechercher par filtre sur le payload
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter={
                    "must": [{"key": "cip13", "match": {"value": cip13}}]
                },
                limit=1,
                with_payload=True,
            )

            if search_result[0]:
                return search_result[0][0].payload

            return None

        except Exception as e:
            print(f"❌ Erreur récupération par CIP: {e}")
            return None

    async def delete_product(self, product_id: int) -> bool:
        """
        Supprimer un produit de l'index.

        Args:
            product_id: ID du produit

        Returns:
            True si succès
        """
        try:
            self.client.delete(
                collection_name=self.collection_name, points_selector=[product_id]
            )

            print(f"🗑️  Produit supprimé de l'index: {product_id}")
            return True

        except Exception as e:
            print(f"❌ Erreur suppression: {e}")
            return False

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Récupérer les infos de la collection.

        Returns:
            Infos de la collection
        """
        try:
            info = self.client.get_collection(self.collection_name)

            return {
                "name": info.config.params.vectors.size,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }

        except Exception as e:
            print(f"❌ Erreur info collection: {e}")
            return {}


# Instance globale
qdrant_client = QdrantClient()