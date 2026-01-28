"""Client OpenAI pour extraction et dialogue."""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI

from src.core.config import settings


class OpenAIClient:
    """Client OpenAI pour LLM."""

    def __init__(self):
        """Initialiser le client OpenAI."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens

    async def extract_order_items(
        self, transcript: str, context: Dict[str, Any]
    ) -> str:
        """
        Extraire les produits et quantités depuis le transcript.

        Args:
            transcript: Transcription de l'audio
            context: Contexte de la conversation

        Returns:
            JSON string avec les produits extraits
        """
        system_prompt = """Tu es un assistant d'extraction de commandes pharmaceutiques.
Extrais les produits et quantités depuis la transcription audio d'un pharmacien.

Format de sortie JSON strict:
{
  "products": [
    {
      "name": "nom du produit",
      "quantity": nombre,
      "unit": "boites" ou "unités"
    }
  ]
}

Règles:
- Si pas de quantité mentionnée, utilise 1
- Si pas d'unité mentionnée, utilise "boites"
- Normalise les noms de produits (enlève les "euh", "donc", etc.)
- Si plusieurs produits, retourne tous dans le tableau
- Si aucun produit détecté, retourne un tableau vide
"""

        conversation_history = context.get("conversation_history", [])
        history_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in conversation_history[-3:]]
        )

        user_prompt = f"""Transcription: {transcript}

Historique récent:
{history_text}

Extrais les produits commandés."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            result = response.choices[0].message.content
            print(f"🤖 LLM Extraction: {result}")

            return result

        except Exception as e:
            print(f"❌ Erreur OpenAI extraction: {e}")
            # Retour par défaut en cas d'erreur
            return json.dumps({"products": []})

    async def generate_response(
        self, user_message: str, conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Générer une réponse conversationnelle.

        Args:
            user_message: Message de l'utilisateur
            conversation_history: Historique de la conversation

        Returns:
            Réponse générée
        """
        system_prompt = """Tu es un agent vocal professionnel pour prendre des commandes pharmaceutiques.

Ton rôle:
- Être concis et clair
- Confirmer les produits commandés
- Demander des clarifications si nécessaire
- Rester professionnel et courtois

Ton style:
- Phrases courtes (max 2 phrases)
- Langage simple et direct
- Pas de jargon technique
- Tutoiement naturel

Exemples de bonnes réponses:
- "D'accord, 10 boites de Doliprane. Autre chose ?"
- "Je n'ai pas bien compris. Vous voulez Spasfon ?"
- "Parfait, je récapitule : 5 Efferalgan, 10 Doliprane. Je valide ?"
"""

        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history[-5:],  # Garder les 5 derniers messages
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Un peu plus créatif pour le dialogue
                max_tokens=150,
            )

            result = response.choices[0].message.content
            print(f"🤖 LLM Response: {result}")

            return result

        except Exception as e:
            print(f"❌ Erreur OpenAI dialogue: {e}")
            return "Excusez-moi, je n'ai pas compris. Pouvez-vous répéter ?"

    async def analyze_intent(self, transcript: str) -> Dict[str, Any]:
        """
        Analyser l'intention de l'utilisateur.

        Args:
            transcript: Transcription de l'audio

        Returns:
            Dict avec l'intention et les paramètres
        """
        system_prompt = """Analyse l'intention du pharmacien dans sa commande.

Intentions possibles:
- "add_product": Ajouter un produit
- "validate_order": Valider la commande
- "modify_order": Modifier un produit
- "cancel": Annuler
- "clarify": Demande de clarification
- "unknown": Intention inconnue

Format de sortie JSON:
{
  "intent": "nom_intention",
  "confidence": 0.0 à 1.0,
  "parameters": {}
}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"❌ Erreur analyse intent: {e}")
            return {"intent": "unknown", "confidence": 0.0, "parameters": {}}

    async def check_validation_keywords(self, transcript: str) -> bool:
        """
        Vérifier si le transcript contient des mots de validation.

        Args:
            transcript: Texte à analyser

        Returns:
            True si validation détectée
        """
        validation_keywords = [
            "c'est tout",
            "je valide",
            "confirme",
            "d'accord",
            "ok",
            "oui",
            "c'est bon",
            "terminé",
            "fini",
            "envoie",
        ]

        transcript_lower = transcript.lower()
        return any(keyword in transcript_lower for keyword in validation_keywords)

    async def summarize_order(self, items: List[Dict[str, Any]]) -> str:
        """
        Créer un résumé naturel de la commande.

        Args:
            items: Liste des items de commande

        Returns:
            Résumé en langage naturel
        """
        if not items:
            return "Aucun produit dans la commande"

        items_text = "\n".join(
            [
                f"- {item.get('quantity')} {item.get('unit', 'boites')} de {item.get('product_name')}"
                for item in items
            ]
        )

        prompt = f"""Résume cette commande de manière naturelle et concise pour confirmation orale:

{items_text}

Fais une phrase courte et claire."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=100,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Erreur résumé: {e}")
            # Fallback simple
            return ", ".join(
                [
                    f"{item['quantity']} {item.get('product_name', 'produit')}"
                    for item in items
                ]
            )