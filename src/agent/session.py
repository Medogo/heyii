"""Gestion des sessions d'appel."""
from typing import Dict, Optional
from datetime import datetime, timedelta

from src.agent.state_machine import ConversationContext


class SessionManager:
    """Gestionnaire de sessions pour les appels actifs."""

    def __init__(self):
        self._sessions: Dict[str, ConversationContext] = {}
        self._session_timeout = timedelta(minutes=30)

    def create_session(self, call_id: str, pharmacy_id: Optional[str] = None) -> ConversationContext:
        """Créer une nouvelle session."""
        context = ConversationContext(call_id=call_id, pharmacy_id=pharmacy_id)
        self._sessions[call_id] = context
        print(f"✅ Session créée: {call_id}")
        return context

    def get_session(self, call_id: str) -> Optional[ConversationContext]:
        """Récupérer une session existante."""
        return self._sessions.get(call_id)

    def delete_session(self, call_id: str) -> bool:
        """Supprimer une session."""
        if call_id in self._sessions:
            del self._sessions[call_id]
            print(f"🗑️  Session supprimée: {call_id}")
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """Nettoyer les sessions expirées."""
        now = datetime.utcnow()
        expired = []

        for call_id, context in self._sessions.items():
            if now - context.last_updated > self._session_timeout:
                expired.append(call_id)

        for call_id in expired:
            self.delete_session(call_id)

        if expired:
            print(f"🧹 {len(expired)} sessions expirées nettoyées")

        return len(expired)

    def get_active_sessions_count(self) -> int:
        """Nombre de sessions actives."""
        return len(self._sessions)

    def get_all_sessions(self) -> Dict[str, ConversationContext]:
        """Récupérer toutes les sessions."""
        return self._sessions.copy()


# Instance globale
session_manager = SessionManager()