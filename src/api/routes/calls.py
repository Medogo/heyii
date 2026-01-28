"""Routes pour la gestion des appels."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import get_db
from src.data.repositories.call_repository import CallRepository
from src.api.schemas.call import CallResponse, CallStats
from src.agent.call_manager import call_manager
from src.agent.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.get("/", response_model=List[CallResponse])
async def list_calls(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    """Lister tous les appels."""
    repo = CallRepository(db)
    calls = await repo.get_all(skip=skip, limit=limit)
    return calls


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
        call_id: str,
        db: AsyncSession = Depends(get_db)
):
    """Récupérer un appel par ID."""
    repo = CallRepository(db)
    call = await repo.get_by_call_id(call_id)

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    return call


@router.get("/active/list")
async def list_active_calls():
    """Lister les appels actifs."""
    return {
        "active_calls": list(call_manager.active_calls.keys()),
        "count": call_manager.get_active_calls_count()
    }


@router.get("/stats/summary", response_model=CallStats)
async def get_call_stats(db: AsyncSession = Depends(get_db)):
    """Statistiques des appels."""
    repo = CallRepository(db)
    stats = await repo.get_stats()
    return stats


@router.delete("/{call_id}")
async def end_call(
        call_id: str,
        db: AsyncSession = Depends(get_db)
):
    """Terminer un appel manuellement."""
    repo = CallRepository(db)
    await call_manager.end_call(call_id, repo, status="ended_manually")

    return {"message": f"Call {call_id} ended"}