from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from packages.db_schema.models import Agent
from app.schemas.entities import AgentCreate, AgentRead

router = APIRouter(prefix="/agents", tags=["Agent Pool"])

@router.post("", response_model=AgentRead)
async def create_agent(payload: AgentCreate, db: AsyncSession = Depends(get_db)):
    agent = Agent(
        name=payload.name,
        role=payload.role,
        backstory=payload.backstory,
        adapter_type=payload.adapter_type,
        model_name=payload.model_name,
        project_tags=payload.project_tags,
        monthly_budget_usd=payload.monthly_budget_usd,
        status="IDLE"
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.get("", response_model=List[AgentRead])
async def list_agents(project_tag: str = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Agent)
    res = await db.execute(stmt)
    agents = res.scalars().all()
    if project_tag:
        agents = [a for a in agents if project_tag in (a.project_tags or [])]
    return agents

@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Agent).where(Agent.id == agent_id)
    res = await db.execute(stmt)
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

from packages.db_schema.models import AgentMessage, Task
from pydantic import BaseModel

class AgentDirectChatRequest(BaseModel):
    message: str

@router.post("/{agent_id}/chat")
async def chat_with_agent(
    agent_id: str,
    payload: AgentDirectChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Engage in direct 1-on-1 dialogue with a specific agent in the pool."""
    agent_res = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = agent_res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    tasks_res = await db.execute(select(Task).where(Task.assigned_agent_id == agent.id))
    assigned_tasks = tasks_res.scalars().all()
    task_summaries = [f"'{t.title}' [{t.status}]" for t in assigned_tasks]

    # Generate persona response
    if "status" in payload.message.lower() or "what are you working on" in payload.message.lower():
        if assigned_tasks:
            resp = f"Hello. As {agent.role}, I am currently assigned to {len(assigned_tasks)} tasks: {', '.join(task_summaries)}. My operational state is {agent.status}."
        else:
            resp = f"Hello. As {agent.role}, I am currently {agent.status} and ready for ticket checkouts matching my tags ({', '.join(agent.project_tags or [])})."
    else:
        resp = f"Acknowledged. I am {agent.name} ({agent.role}). {agent.backstory or 'Standing by for execution directives.'} Current status: {agent.status}."

    # Save to history
    db.add(AgentMessage(
        agent_id=agent.id,
        sender_type="USER",
        message=payload.message,
        message_type="CHAT"
    ))
    db.add(AgentMessage(
        agent_id=agent.id,
        sender_type="AGENT",
        message=resp,
        message_type="CHAT"
    ))
    await db.commit()

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "role": agent.role,
        "status": agent.status,
        "response": resp,
        "assigned_tasks": [t.title for t in assigned_tasks]
    }

@router.get("/{agent_id}/messages")
async def get_agent_messages(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve message history for an agent."""
    stmt = select(AgentMessage).where(AgentMessage.agent_id == agent_id).order_by(AgentMessage.created_at.asc())
    res = await db.execute(stmt)
    messages = res.scalars().all()
    return [
        {
            "id": m.id,
            "sender_type": m.sender_type,
            "message": m.message,
            "message_type": m.message_type,
            "created_at": str(m.created_at)
        }
        for m in messages
    ]

