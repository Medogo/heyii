"""Client pour l'intégration ERP."""
import httpx
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings


class ERPClient:
    """Client pour communiquer avec l'ERP."""

    def __init__(self):
        self.base_url = settings.erp_api_url
        self.api_key = settings.erp_api_key
        self.timeout = settings.erp_timeout

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer une commande dans l'ERP."""

        endpoint = f"{self.base_url}/api/orders/create"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=order_data,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            result = response.json()
            print(f"✅ ERP Order créée: {result.get('order_id')}")

            return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def search_product(
            self,
            query: str,
            fuzzy: bool = True
    ) -> List[Dict[str, Any]]:
        """Rechercher un produit dans le catalogue ERP."""

        endpoint = f"{self.base_url}/api/products/search"
        params = {
            "query": query,
            "fuzzy": str(fuzzy).lower(),
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint,
                params=params,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            result = response.json()
            return result.get("results", [])

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def check_availability(
            self,
            items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Vérifier la disponibilité des produits."""

        endpoint = f"{self.base_url}/api/products/check-availability"

        payload = {"items": items}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return response.json()

    async def get_order_status(self, erp_order_id: str) -> Dict[str, Any]:
        """Récupérer le statut d'une commande dans l'ERP."""

        endpoint = f"{self.base_url}/api/orders/{erp_order_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return response.json()

    async def sync_stock(self, cip13: str) -> int:
        """Synchroniser le stock d'un produit depuis l'ERP."""

        endpoint = f"{self.base_url}/api/products/{cip13}/stock"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            result = response.json()
            return result.get("stock_available", 0)