
# ========================================
# scripts/test_services.py
# ========================================
"""Script pour tester les services IA."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.llm.openai_client import OpenAIClient
from src.services.vector_db.qdrant_client import qdrant_client


async def test_llm():
    """Tester le client LLM."""
    print("\n🤖 Test OpenAI Client")

    client = OpenAIClient()

    # Test extraction
    transcript = "Je voudrais 10 boites de Doliprane 1000 et 5 Spasfon"
    result = await client.extract_order_items(transcript, {})

    print(f"Transcript: {transcript}")
    print(f"Extraction: {result}")


async def test_qdrant():
    """Tester Qdrant."""
    print("\n🔍 Test Qdrant Client")

    # Initialiser
    await qdrant_client.initialize_collection()

    # Rechercher
    results = await qdrant_client.search_product("doliprane", limit=3)

    print(f"Recherche 'doliprane': {len(results)} résultats")
    for i, result in enumerate(results, 1):
        product = result["product"]
        score = result["score"]
        print(f"  {i}. {product['name']} (score: {score:.2f})")


async def main():
    """Main."""
    print("🧪 Tests des services IA")

    await test_llm()
    await test_qdrant()

    print("\n✅ Tests terminés")


if __name__ == "__main__":
    asyncio.run(main())

