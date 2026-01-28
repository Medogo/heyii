"""Service de validation des règles métier."""
from typing import Dict, Any, List, Tuple


class ValidationService:
    """Service de validation des commandes."""

    @staticmethod
    def validate_order_data(order_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Valider les données d'une commande."""

        errors = []

        # Vérifier les champs obligatoires
        if not order_data.get("pharmacy_id"):
            errors.append("pharmacy_id requis")

        if not order_data.get("items") or len(order_data["items"]) == 0:
            errors.append("Au moins un item requis")

        # Valider chaque item
        for i, item in enumerate(order_data.get("items", [])):
            item_errors = ValidationService.validate_order_item(item)
            for error in item_errors:
                errors.append(f"Item {i + 1}: {error}")

        is_valid = len(errors) == 0

        return is_valid, errors

    @staticmethod
    def validate_order_item(item: Dict[str, Any]) -> List[str]:
        """Valider un item de commande."""

        errors = []

        if not item.get("product_cip"):
            errors.append("product_cip requis")

        quantity = item.get("quantity", 0)
        if quantity <= 0:
            errors.append("quantity doit être > 0")

        if quantity > 1000:
            errors.append("quantity maximum dépassée (1000)")

        return errors

    @staticmethod
    def validate_stock_levels(
            items: List[Dict[str, Any]],
            stock_data: Dict[str, int]
    ) -> Tuple[bool, List[str]]:
        """Valider que les stocks sont suffisants."""

        errors = []

        for item in items:
            cip = item.get("product_cip")
            quantity = item.get("quantity", 0)

            available = stock_data.get(cip, 0)

            if available < quantity:
                errors.append(
                    f"Stock insuffisant pour {cip}: "
                    f"demandé {quantity}, disponible {available}"
                )

        is_valid = len(errors) == 0

        return is_valid, errors