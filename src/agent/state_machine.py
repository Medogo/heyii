"""Machine d'états pour la conversation."""
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime


class ConversationState(str, Enum):
    """États possibles de la conversation."""

    IDLE = "idle"
    GREETING = "greeting"
    COLLECTING = "collecting"
    CLARIFYING = "clarifying"
    CONFIRMING = "confirming"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    TRANSFERRING = "transferring"


class ConversationContext:
    """Contexte de la conversation."""

    def __init__(self, call_id: str, pharmacy_id: Optional[str] = None):
        self.call_id = call_id
        self.pharmacy_id = pharmacy_id
        self.state = ConversationState.IDLE
        self.items: list[Dict[str, Any]] = []
        self.current_transcript = ""
        self.conversation_history: list[Dict[str, str]] = []
        self.attempts = 0
        self.confidence_scores: list[float] = []
        self.metadata: Dict[str, Any] = {}
        self.started_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()

    def add_item(self, item: Dict[str, Any]) -> None:
        """Ajouter un item à la commande."""
        self.items.append(item)
        self.last_updated = datetime.utcnow()

    def add_message(self, role: str, content: str) -> None:
        """Ajouter un message à l'historique."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.last_updated = datetime.utcnow()

    def update_state(self, new_state: ConversationState) -> None:
        """Mettre à jour l'état."""
        self.state = new_state
        self.last_updated = datetime.utcnow()

    def increment_attempts(self) -> int:
        """Incrémenter le compteur de tentatives."""
        self.attempts += 1
        return self.attempts

    def get_average_confidence(self) -> float:
        """Calculer la confiance moyenne."""
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)

    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "call_id": self.call_id,
            "pharmacy_id": self.pharmacy_id,
            "state": self.state,
            "items": self.items,
            "conversation_history": self.conversation_history,
            "attempts": self.attempts,
            "average_confidence": self.get_average_confidence(),
            "started_at": self.started_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class StateMachine:
    """Machine d'états pour gérer les transitions."""

    # Transitions autorisées
    TRANSITIONS = {
        ConversationState.IDLE: [ConversationState.GREETING],
        ConversationState.GREETING: [ConversationState.COLLECTING, ConversationState.ERROR],
        ConversationState.COLLECTING: [
            ConversationState.COLLECTING,  # Continue à collecter
            ConversationState.CLARIFYING,  # Besoin de clarification
            ConversationState.CONFIRMING,  # Prêt à confirmer
            ConversationState.ERROR,  # Erreur
            ConversationState.TRANSFERRING,  # Transfer humain
        ],
        ConversationState.CLARIFYING: [
            ConversationState.COLLECTING,
            ConversationState.CONFIRMING,
            ConversationState.TRANSFERRING,
        ],
        ConversationState.CONFIRMING: [
            ConversationState.PROCESSING,
            ConversationState.COLLECTING,  # Ajout d'items
            ConversationState.ERROR,
        ],
        ConversationState.PROCESSING: [
            ConversationState.COMPLETED,
            ConversationState.ERROR,
        ],
        ConversationState.COMPLETED: [],
        ConversationState.ERROR: [ConversationState.TRANSFERRING],
        ConversationState.TRANSFERRING: [],
    }

    def __init__(self, context: ConversationContext):
        self.context = context

    def can_transition(self, to_state: ConversationState) -> bool:
        """Vérifier si la transition est autorisée."""
        current_state = self.context.state
        allowed_states = self.TRANSITIONS.get(current_state, [])
        return to_state in allowed_states

    def transition(self, to_state: ConversationState, reason: str = "") -> bool:
        """Effectuer une transition d'état."""
        if not self.can_transition(to_state):
            print(f"⚠️  Transition non autorisée: {self.context.state} -> {to_state}")
            return False

        print(f"🔄 Transition: {self.context.state} -> {to_state} ({reason})")
        self.context.update_state(to_state)
        return True

    def should_transfer_to_human(self) -> bool:
        """Déterminer si on doit transférer à un humain."""
        # Trop de tentatives
        if self.context.attempts >= 3:
            return True

        # Confiance trop basse
        avg_confidence = self.context.get_average_confidence()
        if avg_confidence > 0 and avg_confidence < 0.70:
            return True

        return False