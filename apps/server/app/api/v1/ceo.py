from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.db.session import get_db
from app.core.ceo_engine import CEOEngine
from packages.db_schema.models import AgentMessage, Team, Agent

router = APIRouter(prefix="/ceo", tags=["CEO Executive Office & Delegation"])

class CEOChatRequest(BaseModel):
    message: str
    project_tag: Optional[str] = None

class CEOChatResponse(BaseModel):
    response: str
    intent: str
    ceo_name: Optional[str] = None
    ceo_role: Optional[str] = None
    actions_taken: List[Dict[str, Any]] = []
    report_data: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=CEOChatResponse)
async def chat_with_ceo(payload: CEOChatRequest, db: AsyncSession = Depends(get_db)):
    """Communicate directly with the CEO / Lead Orchestrator agent to assign goals, request reports, and delegate work."""
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Directive message cannot be empty")
    
    result = await CEOEngine.process_ceo_directive(
        db=db,
        user_message=payload.message,
        project_tag=payload.project_tag
    )
    return CEOChatResponse(**result)


@router.get("/history")
async def get_ceo_chat_history(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Fetch conversation history between the user and the CEO."""
    team_res = await db.execute(select(Team).order_by(Team.created_at.desc()).limit(1))
    team = team_res.scalar_one_or_none()
    if not team or not team.lead_agent_id:
        return []

    msg_res = await db.execute(
        select(AgentMessage)
        .where(AgentMessage.agent_id == team.lead_agent_id)
        .order_by(AgentMessage.created_at.asc())
        .limit(limit)
    )
    messages = msg_res.scalars().all()
    return [
        {
            "id": m.id,
            "sender_type": m.sender_type,
            "message": m.message,
            "message_type": m.message_type,
            "metadata": m.metadata_payload,
            "created_at": str(m.created_at)
        }
        for m in messages
    ]
