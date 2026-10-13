from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.db.session import get_db
from packages.db_schema.models import Team, TeamMembership, Agent
from app.schemas.entities import TeamCreate, TeamRead, CompileTeamRequest, TeamMemberInfo

router = APIRouter(prefix="/teams", tags=["Dynamic Team Compilation"])

@router.post("/compile", response_model=TeamRead)
async def compile_team(payload: CompileTeamRequest, db: AsyncSession = Depends(get_db)):
    lead_stmt = select(Agent).where(Agent.id == payload.lead_agent_id)
    lead_res = await db.execute(lead_stmt)
    lead = lead_res.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead agent not found")

    team = Team(
        name=payload.name,
        project_tag=payload.project_tag,
        lead_agent_id=payload.lead_agent_id
    )
    db.add(team)
    await db.flush()

    lead_mem = TeamMembership(team_id=team.id, agent_id=lead.id, team_role="Lead")
    db.add(lead_mem)

    members_info = [
        TeamMemberInfo(agent_id=lead.id, agent_name=lead.name, role=lead.role, team_role="Lead")
    ]

    for item in payload.member_assignments:
        ag_id = item.get("agent_id")
        t_role = item.get("team_role", "Specialist")
        if ag_id == lead.id:
            continue

        ag_stmt = select(Agent).where(Agent.id == ag_id)
        ag_res = await db.execute(ag_stmt)
        ag = ag_res.scalar_one_or_none()
        if ag:
            mem = TeamMembership(team_id=team.id, agent_id=ag.id, team_role=t_role)
            db.add(mem)
            members_info.append(
                TeamMemberInfo(agent_id=ag.id, agent_name=ag.name, role=ag.role, team_role=t_role)
            )

    await db.commit()
    await db.refresh(team)

    return TeamRead(
        id=team.id,
        name=team.name,
        project_tag=team.project_tag,
        lead_agent_id=team.lead_agent_id,
        members=members_info,
        created_at=team.created_at
    )

@router.get("", response_model=List[TeamRead])
async def list_teams(db: AsyncSession = Depends(get_db)):
    stmt = select(Team).options(selectinload(Team.members).selectinload(TeamMembership.agent))
    res = await db.execute(stmt)
    teams = res.scalars().all()

    result = []
    for t in teams:
        members_info = []
        for m in t.members:
            if m.agent:
                members_info.append(
                    TeamMemberInfo(
                        agent_id=m.agent.id,
                        agent_name=m.agent.name,
                        role=m.agent.role,
                        team_role=m.team_role
                    )
                )
        result.append(
            TeamRead(
                id=t.id,
                name=t.name,
                project_tag=t.project_tag,
                lead_agent_id=t.lead_agent_id,
                members=members_info,
                created_at=t.created_at
            )
        )
    return result
