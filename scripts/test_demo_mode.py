
# ========================================
# scripts/test_demo_mode.py
# ========================================
"""Script pour tester le mode démo."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.demo.demo_order_service import DemoOrderService


async def test_demo_order():
    """Tester une commande en mode démo."""
    print("🎭 TEST MODE DÉMO")
    print("=" * 50)

    # Initialiser le service démo
    demo_service = DemoOrderService(
        notification_emails=["test@example.com"],
        notification_whatsapp="+22900000000",
    )

    # Simuler des items
    items = [
        {
            "product_name": "DOLIPRANE 1000MG CPR SEC 8",
            "product_cip": "3400934823432",
            "quantity": 10,
            "unit": "boites",
            "unit_price": 5.50,
        },
        {
            "product_name": "SPASFON LYOC 80MG",
            "product_cip": "3400892567123",
            "quantity": 5,
            "unit": "boites",
            "unit_price": 8.20,
        },
    ]

    # Créer une commande
    result = await demo_service.create_order(
        call_id="test-call-001",
        pharmacy_id="pharma_0001",
        pharmacy_name="Pharmacie Test",
        items=items,
        confidence=0.95,
    )

    print("\n✅ RÉSULTAT:")
    print(f"Order ID: {result['order_id']}")
    print(f"Total: {result['total_amount']:.2f} €")
    print(f"Notifications envoyées: {result['notifications_sent']}")
    print(f"Mode: {result['mode']}")
    print(f"Message: {result['message']}")

    # Récupérer toutes les commandes
    all_orders = await demo_service.get_all_demo_orders()
    print(f"\n📦 Total commandes démo: {len(all_orders)}")


if __name__ == "__main__":
    asyncio.run(test_demo_order())