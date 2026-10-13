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
