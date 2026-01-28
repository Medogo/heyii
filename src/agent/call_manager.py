"""Gestionnaire des appels téléphoniques."""
import asyncio
from typing import Optional, Callable
from datetime import datetime

from src.agent.session import session_manager, ConversationContext
from src.agent.state_machine import StateMachine, ConversationState
from src.data.models import Call
from src.data.repositories.call_repository import CallRepository


class CallManager:
    """Gère le cycle de vie des appels."""

    def __init__(self):
        self.active_calls: dict[str, dict] = {}
        self.max_concurrent_calls = 10

    async def start_call(
            self,
            call_id: str,
            phone_number: str,
            call_repository: CallRepository,
    ) -> ConversationContext:
        """Démarrer un nouvel appel."""

        # Vérifier la capacité
        if len(self.active_calls) >= self.max_concurrent_calls:
            raise Exception(f"Maximum concurrent calls reached: {self.max_concurrent_calls}")

        # Créer la session
        context = session_manager.create_session(call_id)

        # Créer l'enregistrement en base
        call = Call(
            call_id=call_id,
            phone_number=phone_number,
            status="active",
            agent_version="1.0.0",
            started_at=datetime.utcnow(),
        )
        await call_repository.create(call)

        # Ajouter aux appels actifs
        self.active_calls[call_id] = {
            "context": context,
            "phone_number": phone_number,
            "started_at": datetime.utcnow(),
        }

        print(f"📞 Appel démarré: {call_id} ({phone_number})")
        print(f"📊 Appels actifs: {len(self.active_calls)}/{self.max_concurrent_calls}")

        return context

    async def end_call(
            self,
            call_id: str,
            call_repository: CallRepository,
            status: str = "completed",
    ) -> None:
        """Terminer un appel."""

        if call_id not in self.active_calls:
            print(f"⚠️  Appel non trouvé: {call_id}")
            return

        # Récupérer les infos
        call_info = self.active_calls[call_id]
        started_at = call_info["started_at"]
        duration = (datetime.utcnow() - started_at).total_seconds()

        # Mettre à jour en base
        call = await call_repository.get_by_call_id(call_id)
        if call:
            call.status = status
            call.ended_at = datetime.utcnow()
            call.duration_seconds = int(duration)
            await call_repository.update(call)

        # Nettoyer
        del self.active_calls[call_id]
        session_manager.delete_session(call_id)

        print(f"📵 Appel terminé: {call_id} (durée: {duration:.1f}s)")
        print(f"📊 Appels actifs: {len(self.active_calls)}/{self.max_concurrent_calls}")

    def get_active_call(self, call_id: str) -> Optional[dict]:
        """Récupérer un appel actif."""
        return self.active_calls.get(call_id)

    def get_active_calls_count(self) -> int:
        """Nombre d'appels actifs."""
        return len(self.active_calls)

    async def cleanup_stale_calls(self, call_repository: CallRepository, timeout_minutes: int = 30):
        """Nettoyer les appels bloqués."""
        now = datetime.utcnow()
        stale_calls = []

        for call_id, call_info in self.active_calls.items():
            started_at = call_info["started_at"]
            duration = (now - started_at).total_seconds() / 60

            if duration > timeout_minutes:
                stale_calls.append(call_id)

        for call_id in stale_calls:
            await self.end_call(call_id, call_repository, status="timeout")

        if stale_calls:
            print(f"🧹 {len(stale_calls)} appels bloqués nettoyés")


# Instance globale
call_manager = CallManager()