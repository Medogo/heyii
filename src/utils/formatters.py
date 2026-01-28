
# ========================================
# src/utils/formatters.py
# ========================================
"""Formateurs de données."""
from datetime import datetime
from typing import Any, Dict


def format_currency(amount: float, currency: str = "€") -> str:
    """
    Formater un montant.

    Args:
        amount: Montant
        currency: Symbole monétaire

    Returns:
        Montant formaté
    """
    return f"{amount:,.2f} {currency}".replace(",", " ")


def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formater une date.

    Args:
        dt: Datetime
        format_str: Format

    Returns:
        Date formatée
    """
    return dt.strftime(format_str)


def format_phone_display(phone: str) -> str:
    """
    Formater un numéro pour affichage.

    Args:
        phone: Numéro brut

    Returns:
        Numéro formaté
    """
    # Exemple: +22900000000 -> +229 00 00 00 00
    if phone.startswith("+229"):
        return f"+229 {phone[4:6]} {phone[6:8]} {phone[8:10]} {phone[10:]}"

    return phone


def format_order_summary(order: Dict[str, Any]) -> str:
    """
    Formater le résumé d'une commande.

    Args:
        order: Données de commande

    Returns:
        Résumé formaté
    """
    items = order.get("items", [])
    total = order.get("total_amount", 0)

    summary_lines = [f"Commande {order.get('order_id')}:"]

    for item in items:
        qty = item.get("quantity", 0)
        name = item.get("product_name", "Produit")
        summary_lines.append(f"- {qty}x {name}")

    summary_lines.append(f"\nTotal: {format_currency(total)}")

    return "\n".join(summary_lines)