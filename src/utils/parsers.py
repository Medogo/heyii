# ========================================
# src/utils/parsers.py
# ========================================
"""Parseurs de données."""
import re
from typing import Tuple, Optional


def parse_quantity_from_text(text: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Extraire quantité et unité depuis un texte.

    Args:
        text: Texte contenant quantité

    Returns:
        (quantité, unité)
    """
    # Patterns courants
    patterns = [
        r"(\d+)\s*(boite|boites|boîte|boîtes)",
        r"(\d+)\s*(unite|unites|unité|unités)",
        r"(\d+)\s*(flacon|flacons)",
        r"(\d+)\s*(tube|tubes)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quantity = int(match.group(1))
            unit = match.group(2).lower()

            # Normaliser l'unité
            if unit in ["boite", "boites", "boîte", "boîtes"]:
                unit = "boites"
            elif unit in ["unite", "unites", "unité", "unités"]:
                unit = "unités"

            return quantity, unit

    # Si pas de pattern trouvé, chercher juste un nombre
    match = re.search(r"(\d+)", text)
    if match:
        return int(match.group(1)), "boites"

    return None, None


def parse_product_name(text: str) -> str:
    """
    Nettoyer et normaliser un nom de produit.

    Args:
        text: Nom brut

    Returns:
        Nom nettoyé
    """
    # Supprimer les mots parasites
    stopwords = ["euh", "donc", "alors", "voilà", "ben"]

    words = text.lower().split()
    cleaned_words = [w for w in words if w not in stopwords]

    return " ".join(cleaned_words).strip()