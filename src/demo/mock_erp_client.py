# 🎭 MODE SIMULATION/TEST SANS ERP - HEYI
# Package séparé pour tester l'agent IA sans connexion ERP réelle

# ========================================
# src/demo/mock_erp_client.py
# ========================================
"""Mock ERP Client pour simulation sans ERP réel."""
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import random


class MockERPClient:
    """
    Client ERP simulé pour tests et démonstration.

    Simule les réponses d'un ERP sans connexion réelle.
    """

    def __init__(self):
        """Initialiser le mock ERP."""
        self.orders = []  # Stockage en mémoire des commandes
        self.order_counter = 1000

    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simuler la création d'une commande dans l'ERP.

        Args:
            order_data: Données de la commande

        Returns:
            Réponse simulée de l'ERP
        """
        # Simuler un petit délai réseau
        await asyncio.sleep(0.5)

        # Générer un ID de commande
        order_id = f"MOCK-{self.order_counter}"
        self.order_counter += 1

        # Calculer le total
        total_amount = sum(
            item.get("line_total", item.get("unit_price", 0) * item.get("quantity", 0))
            for item in order_data.get("items", [])
        )

        # Créer la commande simulée
        mock_order = {
            "success": True,
            "order_id": order_id,
            "total_amount": total_amount,
            "delivery_date": order_data.get("delivery_date"),
            "status": "pending_preparation",
            "created_at": datetime.utcnow().isoformat(),
            "message": "✅ Commande créée avec succès (MODE SIMULATION)",
        }

        # Stocker en mémoire
        self.orders.append({
            **mock_order,
            "order_data": order_data,
        })

        print(f"🎭 MOCK ERP: Commande créée - {order_id}")

        return mock_order

    async def search_product(
            self, query: str, fuzzy: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Simuler la recherche de produit.

        Args:
            query: Requête de recherche
            fuzzy: Recherche floue

        Returns:
            Résultats simulés
        """
        await asyncio.sleep(0.2)

        # Produits simulés courants
        mock_products = [
            {
                "cip13": "3400934823432",
                "name": "DOLIPRANE 1000MG CPR SEC 8",
                "stock_available": 2000,
                "price": 5.50,
                "match_score": 0.95,
            },
            {
                "cip13": "3400892567123",
                "name": "SPASFON LYOC 80MG",
                "stock_available": 500,
                "price": 8.20,
                "match_score": 0.92,
            },
            {
                "cip13": "3400935467891",
                "name": "EFFERALGAN 1G CPR EFF 8",
                "stock_available": 1500,
                "price": 4.80,
                "match_score": 0.90,
            },
        ]

        # Filtrer selon la requête (simple)
        query_lower = query.lower()
        results = [
            p for p in mock_products
            if query_lower in p["name"].lower()
        ]

        return {"results": results[:3]}

    async def check_availability(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simuler la vérification de disponibilité.

        Args:
            items: Items à vérifier

        Returns:
            Statut de disponibilité
        """
        await asyncio.sleep(0.3)

        items_status = []
        for item in items:
            # Simuler disponibilité (90% de chance disponible)
            is_available = random.random() > 0.1

            items_status.append({
                "cip13": item.get("cip13"),
                "requested": item.get("quantity"),
                "available": 1000 if is_available else 0,
                "status": "ok" if is_available else "out_of_stock",
            })

        return {
            "available": all(item["status"] == "ok" for item in items_status),
            "items_status": items_status,
        }

    async def get_order_status(self, erp_order_id: str) -> Dict[str, Any]:
        """
        Simuler la récupération du statut.

        Args:
            erp_order_id: ID de la commande

        Returns:
            Statut de la commande
        """
        await asyncio.sleep(0.2)

        # Chercher dans les commandes stockées
        for order in self.orders:
            if order["order_id"] == erp_order_id:
                return {
                    "order_id": order["order_id"],
                    "status": "processing",
                    "total_amount": order["total_amount"],
                }

        return {
            "order_id": erp_order_id,
            "status": "not_found",
        }

    async def sync_stock(self, cip13: str) -> int:
        """
        Simuler la synchro stock.

        Args:
            cip13: Code CIP

        Returns:
            Stock disponible
        """
        await asyncio.sleep(0.2)

        # Stock aléatoire entre 0 et 2000
        return random.randint(100, 2000)

    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Récupérer toutes les commandes simulées."""
        return self.orders


# ========================================
# src/core/config.py - AJOUTER
# ========================================
"""
# Ajouter dans la classe Settings:

class Settings(BaseSettings):
    # ... configs existantes ...

    
"""

# ========================================
# .env - AJOUTER
# ========================================
"""
"""

# ========================================
# src/business/order_service.py - MODIFIER
# ========================================
"""
# Dans le OrderService existant, ajouter en début de create_order():

async def create_order(self, ...):
    '''Créer une nouvelle commande.'''

    # MODE DÉMO: Utiliser le service démo au lieu de l'ERP réel
    if settings.demo_mode:
        from src.demo.demo_order_service import DemoOrderService

        demo_service = DemoOrderService(
            notification_emails=settings.demo_emails_list,
            notification_whatsapp=settings.demo_notification_whatsapp,
        )

        return await demo_service.create_order(
            call_id=call_id,
            pharmacy_id=pharmacy_id,
            pharmacy_name=pharmacy_name,  # À passer en param
            items=items,
            confidence=confidence,
        )

    # MODE PRODUCTION: Code existant...
    # ... reste du code normal ...
"""
