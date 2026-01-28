

# ========================================
# src/utils/validators.py
# ========================================
"""Validateurs de données."""
import re
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """
    Valider un numéro de téléphone.

    Args:
        phone: Numéro de téléphone

    Returns:
        True si valide
    """
    # Format international simple
    pattern = r"^\+?[1-9]\d{1,14}$"
    return bool(re.match(pattern, phone))


def validate_cip13(cip13: str) -> bool:
    """
    Valider un code CIP13.

    Args:
        cip13: Code CIP

    Returns:
        True si valide
    """
    return len(cip13) == 13 and cip13.isdigit()


def validate_email(email: str) -> bool:
    """
    Valider une adresse email.

    Args:
        email: Email

    Returns:
        True si valide
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def sanitize_text(text: str) -> str:
    """
    Nettoyer un texte.

    Args:
        text: Texte brut

    Returns:
        Texte nettoyé
    """
    # Supprimer les caractères spéciaux
    text = re.sub(r"[^\w\s\-.,!?àâäéèêëïîôùûüÿœæç]", "", text, flags=re.IGNORECASE)

    # Normaliser les espaces
    text = " ".join(text.split())

    return text.strip()
