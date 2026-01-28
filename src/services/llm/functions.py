
# ========================================
# src/services/llm/functions.py
# ========================================
"""Schémas de Function Calling pour OpenAI."""

FUNCTION_SCHEMAS = {
    "extract_order": {
        "name": "extract_order",
        "description": "Extraire les produits et quantités d'une commande",
        "parameters": {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "description": "Liste des produits commandés",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Nom du produit",
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "Quantité",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["boites", "unités", "flacons"],
                                "description": "Unité",
                            },
                        },
                        "required": ["name", "quantity"],
                    },
                }
            },
            "required": ["products"],
        },
    },
    "search_product": {
        "name": "search_product",
        "description": "Rechercher un produit dans le catalogue",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Nom du produit à rechercher",
                }
            },
            "required": ["query"],
        },
    },
}