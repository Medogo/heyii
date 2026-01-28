"""Mapper pour transformer les données entre HEYI et l'ERP."""
from typing import Dict, Any, List
from datetime import datetime

from src.data.models import Order, OrderItem, Product


class ERPMapper:
    """Mapper pour convertir les données."""

    @staticmethod
    def order_to_erp(order: Order) -> Dict[str, Any]:
        """Convertir une commande HEYI vers format ERP."""

        return {
            "pharmacy_id": order.pharmacy.pharmacy_id,
            "order_date": order.created_at.isoformat(),
            "items": [
                ERPMapper.order_item_to_erp(item)
                for item in order.items
            ],
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
            "notes": order.delivery_notes,
            "source": "agent_ia_v1",
            "external_order_id": order.order_id,
            "total_amount": order.total_amount,
        }

    @staticmethod
    def order_item_to_erp(item: OrderItem) -> Dict[str, Any]:
        """Convertir un item de commande vers format ERP."""

        return {
            "product_cip13": item.product.cip13,
            "quantity": item.quantity_asked,
            "unit_price": item.unit_price,
            "line_total": item.line_total,
        }

    @staticmethod
    def erp_product_to_heyi(erp_product: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir un produit ERP vers format HEYI."""

        return {
            "cip13": erp_product.get("cip13"),
            "ean": erp_product.get("ean"),
            "name": erp_product.get("name"),
            "category": erp_product.get("category"),
            "supplier_code": erp_product.get("supplier_code"),
            "unit_price": erp_product.get("price", 0.0),
            "stock_available": erp_product.get("stock_available", 0),
        }