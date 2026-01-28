"""Gestionnaire de dialogue pour générer les réponses appropriées."""
from typing import Dict, Any
from src.agent.state_machine import ConversationState


class DialogueManager:
    """Gère la génération des réponses selon le contexte."""

    # Templates de réponses
    TEMPLATES = {
        ConversationState.GREETING: [
            "Bonjour, bienvenue chez {company}. Vous pouvez me dicter votre commande.",
            "Bonjour, je vous écoute pour votre commande.",
        ],

        ConversationState.COLLECTING: [
            "Bien noté, {quantity} {unit} de {product}. Autre chose ?",
            "D'accord, j'ai ajouté {quantity} {unit} de {product}. Continuez.",
            "Parfait. Autre produit à commander ?",
        ],

        ConversationState.CLARIFYING: [
            "Excusez-moi, pouvez-vous répéter le nom du produit ?",
            "Je n'ai pas bien compris. Vous parliez de {suggestion} ?",
            "Voulez-vous dire {suggestion} ou autre chose ?",
        ],

        ConversationState.CONFIRMING: [
            "Récapitulatif de votre commande : {recap}. Je valide ?",
            "Voici ce que j'ai noté : {recap}. Confirmez-vous ?",
        ],

        ConversationState.COMPLETED: [
            "Commande validée, numéro {order_id}. Merci et bonne journée !",
            "Parfait ! Votre commande {order_id} est enregistrée. Au revoir !",
        ],

        ConversationState.ERROR: [
            "Désolé, je rencontre un problème technique. Un instant...",
            "Excusez-moi, je vais vous transférer à un conseiller.",
        ],

        ConversationState.TRANSFERRING: [
            "Je vous transfère à un conseiller. Un instant s'il vous plaît...",
        ],
    }

    def __init__(self, company_name: str = "votre grossiste pharmaceutique"):
        self.company_name = company_name

    def generate_response(
            self,
            state: ConversationState,
            context: Dict[str, Any] = None
    ) -> str:
        """Générer une réponse appropriée selon l'état."""
        context = context or {}
        templates = self.TEMPLATES.get(state, [""])

        if not templates:
            return "Je vous écoute."

        # Choisir le premier template (ou faire random plus tard)
        template = templates[0]

        # Remplacer les variables
        response = template.format(
            company=self.company_name,
            **context
        )

        return response

    def format_recap(self, items: list[Dict[str, Any]]) -> str:
        """Formater le récapitulatif de commande."""
        if not items:
            return "Aucun produit"

        recap_parts = []
        for item in items:
            product_name = item.get("product_name", "produit")
            quantity = item.get("quantity", 0)
            unit = item.get("unit", "unités")
            recap_parts.append(f"{quantity} {unit} de {product_name}")

        return ", ".join(recap_parts)

    def generate_out_of_stock_message(self, product_name: str, alternative: str = None) -> str:
        """Message pour rupture de stock."""
        base = f"Désolé, {product_name} est actuellement en rupture de stock."
        if alternative:
            return f"{base} Souhaitez-vous {alternative} à la place ?"
        return f"{base} Voulez-vous commander autre chose ?"

    def generate_product_not_found_message(self, query: str, suggestions: list[str] = None) -> str:
        """Message quand produit non trouvé."""
        base = f"Je n'ai pas trouvé '{query}' dans notre catalogue."

        if suggestions:
            suggestions_text = " ou ".join(suggestions[:3])
            return f"{base} Parliez-vous de {suggestions_text} ?"

        return f"{base} Pouvez-vous préciser le nom complet ?"


# Instance globale
dialogue_manager = DialogueManager()