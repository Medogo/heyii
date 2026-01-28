
# ========================================
# src/services/llm/base.py
# ========================================
"""Interface de base pour les services LLM."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseLLMClient(ABC):
    """Interface de base pour les clients LLM."""

    @abstractmethod
    async def extract_order_items(
            self, transcript: str, context: Dict[str, Any]
    ) -> str:
        """Extraire les items de commande."""
        pass

    @abstractmethod
    async def generate_response(
            self, user_message: str, conversation_history: List[Dict[str, str]]
    ) -> str:
        """Générer une réponse conversationnelle."""
        pass

    @abstractmethod
    async def analyze_intent(self, transcript: str) -> Dict[str, Any]:
        """Analyser l'intention."""
        pass
