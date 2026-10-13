from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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

from packages.db_schema.models import Advisor, Task

@router.get("/hierarchy")
async def get_team_hierarchy(db: AsyncSession = Depends(get_db)):
    """Retrieve full organizational hierarchy: CEO -> Advisors Council -> Teams/Squads -> Member Agents."""
    team_stmt = select(Team).options(
        selectinload(Team.members).selectinload(TeamMembership.agent),
        selectinload(Team.lead_agent)
    ).order_by(Team.created_at.desc())
    res = await db.execute(team_stmt)
    all_teams = res.scalars().all()

    # Primary org / team
    primary_team = all_teams[0] if all_teams else None
    company_name = primary_team.name if primary_team else "Folks Organization"
    mission = primary_team.mission if primary_team else ""
    project_tag = primary_team.project_tag if primary_team else "folks_core"

    # CEO Agent
    ceo = None
    if primary_team and primary_team.lead_agent:
        ceo = {
            "id": primary_team.lead_agent.id,
            "name": primary_team.lead_agent.name,
            "role": primary_team.lead_agent.role,
            "status": primary_team.lead_agent.status,
            "model_name": primary_team.lead_agent.model_name,
            "adapter_type": primary_team.lead_agent.adapter_type,
            "monthly_budget_usd": float(primary_team.lead_agent.monthly_budget_usd or 0)
        }

    # Strategic Board of Advisors
    adv_res = await db.execute(select(Advisor))
    advisors_list = adv_res.scalars().all()
    advisors = [
        {
            "id": a.id,
            "name": a.name,
            "domain": a.domain,
            "reasoning_model": a.reasoning_model,
            "status": a.status
        }
        for a in advisors_list
    ]

    # Squads and Member mapping
    teams_data = []
    for t in all_teams:
        members_list = []
        for m in t.members:
            if m.agent:
                # Count tasks for this agent
                agent_tasks_count = (await db.execute(
                    select(func.count(Task.id)).where(Task.assigned_agent_id == m.agent.id)
                )).scalar() or 0
                members_list.append({
                    "id": m.agent.id,
                    "name": m.agent.name,
                    "role": m.agent.role,
                    "team_role": m.team_role,
                    "status": m.agent.status,
                    "model_name": m.agent.model_name,
                    "assigned_tasks_count": agent_tasks_count
                })

        team_tasks_count = (await db.execute(
            select(func.count(Task.id)).where(Task.team_id == t.id)
        )).scalar() or 0

        teams_data.append({
            "id": t.id,
            "name": t.name,
            "project_tag": t.project_tag,
            "lead_agent": {
                "id": t.lead_agent.id,
                "name": t.lead_agent.name,
                "role": t.lead_agent.role
            } if t.lead_agent else None,
            "members": members_list,
            "tasks_count": team_tasks_count
        })

    return {
        "company_name": company_name,
        "mission": mission,
        "project_tag": project_tag,
        "ceo": ceo,
        "advisors": advisors,
        "teams": teams_data
    }

