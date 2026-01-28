"""Fichiers finaux - Monitoring et ERP."""

# ========================================
# src/integrations/erp/base.py
# ========================================
"""Interface de base pour les clients ERP."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseERPClient(ABC):
    """Interface de base pour les clients ERP."""

    @abstractmethod
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer une commande dans l'ERP."""
        pass

    @abstractmethod
    async def search_product(
            self, query: str, fuzzy: bool = True
    ) -> List[Dict[str, Any]]:
        """Rechercher un produit."""
        pass

    @abstractmethod
    async def check_availability(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Vérifier la disponibilité."""
        pass

    @abstractmethod
    async def get_order_status(self, erp_order_id: str) -> Dict[str, Any]:
        """Récupérer le statut d'une commande."""
        pass

    @abstractmethod
    async def sync_stock(self, cip13: str) -> int:
        """Synchroniser le stock."""
        pass

