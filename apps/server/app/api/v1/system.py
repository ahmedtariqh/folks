from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List
from datetime import timedelta

from app.db.session import get_db
from packages.db_schema.models import (
    Agent, Team, TeamMembership, Task, KnowledgeBase, Advisor,
    AdvisorKnowledgeLink, WarRoom, AuditLog, utc_now
)
from app.core.config import settings

router = APIRouter(prefix="/system", tags=["System Management & Overview"])

@router.get("/overview")
async def get_system_overview(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve full platform health, state-machine telemetry, and queue metrics."""
    # Count agents
    agent_count_res = await db.execute(select(func.count(Agent.id)))
    agent_count = agent_count_res.scalar() or 0

    # Count teams
    team_count_res = await db.execute(select(func.count(Team.id)))
    team_count = team_count_res.scalar() or 0

    # Tasks breakdown
    task_stmt = select(Task.status, func.count(Task.id)).group_by(Task.status)
    task_res = await db.execute(task_stmt)
    tasks_by_status = {row[0]: row[1] for row in task_res.all()}

    total_tasks = sum(tasks_by_status.values())
    in_progress = tasks_by_status.get("IN_PROGRESS", 0)
    paused = tasks_by_status.get("PAUSED_FOR_CONSULTATION", 0)
    dlq = tasks_by_status.get("DEAD_LETTER_QUEUE", 0)
    completed = tasks_by_status.get("DONE", 0) + tasks_by_status.get("COMPLETED", 0)
    backlog = tasks_by_status.get("BACKLOG", 0) + tasks_by_status.get("TODO", 0) + tasks_by_status.get("QUEUED", 0)

    # Count War Rooms
    war_room_res = await db.execute(select(func.count(WarRoom.id)))
    war_room_count = war_room_res.scalar() or 0

    # Count Advisors
    advisor_res = await db.execute(select(func.count(Advisor.id)))
    advisor_count = advisor_res.scalar() or 0

    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "sweeper": {
            "status": "ACTIVE",
            "heartbeat_interval_seconds": 15,
            "lock_ttl_seconds": 60,
            "reaper_mode": "AUTO_DLQ"
        },
        "metrics": {
            "agents_total": agent_count,
            "teams_total": team_count,
            "advisors_total": advisor_count,
            "war_rooms_total": war_room_count,
            "tasks": {
                "total": total_tasks,
                "backlog": backlog,
                "in_progress": in_progress,
                "paused_for_consultation": paused,
                "dlq": dlq,
                "completed": completed,
                "by_status": tasks_by_status
            }
        }
    }


@router.post("/seed")
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    """Seed sample team, agents, advisory board, and Kanban tasks for immediate interactive demo."""
    # Check if team already exists
    existing_team = (await db.execute(select(Team).where(Team.project_tag == "folks_core"))).scalar_one_or_none()
    
    if not existing_team:
        team = Team(name="Core Platform Engineering", project_tag="folks_core")
        db.add(team)
        await db.flush()
    else:
        team = existing_team

    # Create Agents if they don't exist
    agent_names = ["Nova - Lead Architect", "Forge - CLI Daemon Specialist", "Cipher - Security Auditor"]
    existing_agents = (await db.execute(select(Agent).where(Agent.name.in_(agent_names)))).scalars().all()
    existing_agent_map = {a.name: a for a in existing_agents}

    agent_nova = existing_agent_map.get("Nova - Lead Architect")
    if not agent_nova:
        agent_nova = Agent(
            name="Nova - Lead Architect",
            role="Lead Architect",
            backstory="Specializes in distributed state machines, hierarchical locks, and system boundaries.",
            model_name="claude-3-7-sonnet",
            adapter_type="host_cli",
            project_tags=["folks_core"],
            status="IDLE"
        )
        db.add(agent_nova)
        await db.flush()
        db.add(TeamMembership(team_id=team.id, agent_id=agent_nova.id, team_role="Lead"))

    agent_forge = existing_agent_map.get("Forge - CLI Daemon Specialist")
    if not agent_forge:
        agent_forge = Agent(
            name="Forge - CLI Daemon Specialist",
            role="CLI Daemon Specialist",
            backstory="Executes local shell commands, drives host test runners, and emits 15s heartbeats.",
            model_name="claude-3-5-sonnet",
            adapter_type="host_cli",
            project_tags=["folks_core"],
            status="IN_PROGRESS"
        )
        db.add(agent_forge)
        await db.flush()
        db.add(TeamMembership(team_id=team.id, agent_id=agent_forge.id, team_role="Specialist"))

    agent_cipher = existing_agent_map.get("Cipher - Security Auditor")
    if not agent_cipher:
        agent_cipher = Agent(
            name="Cipher - Security Auditor",
            role="Security Auditor",
            backstory="Verifies Copilot API boundary enforcement, zero SQL execution rules, and RBAC.",
            model_name="claude-3-5-sonnet",
            adapter_type="host_cli",
            project_tags=["folks_core"],
            status="IDLE"
        )
        db.add(agent_cipher)
        await db.flush()
        db.add(TeamMembership(team_id=team.id, agent_id=agent_cipher.id, team_role="Auditor"))

    await db.flush()

    # Create Knowledge Bases & Board of Advisors
    existing_kb = (await db.execute(select(KnowledgeBase).where(KnowledgeBase.domain_tag == "distributed_systems"))).scalar_one_or_none()
    if not existing_kb:
        kb_dist = KnowledgeBase(
            name="Distributed Consensus & Lock Lease Invariants",
            domain_tag="distributed_systems",
            description="Deep architecture documentation on distributed locks, fencing tokens, and split-brain resolution.",
            documents=[
                {
                    "title": "TTL Sweeper & Heartbeat Guarantees",
                    "content": "Locks must expire deterministically after 60 seconds if heartbeat pings (every 15s) are missed. Expired tasks MUST shift to DEAD_LETTER_QUEUE to prevent zombie resource leaks."
                },
                {
                    "title": "Hierarchical Sub-Routine Isolation",
                    "content": "Kanban locks remain primary. War Rooms are ephemeral subroutines. Lock suspension freezes TTL while preserving task assignment."
                }
            ]
        )
        db.add(kb_dist)
        await db.flush()

        advisor_dist = Advisor(
            name="Dr. Aris Thorne",
            domain="DISTRIBUTED_SYSTEMS",
            reasoning_model="claude-3-7-sonnet-thought",
            system_prompt="You are Dr. Thorne, Senior Advisor on Distributed Consensus and Lock Invariants. Provide multi-perspective deep reasoning.",
            status="ACTIVE"
        )
        db.add(advisor_dist)
        await db.flush()
        db.add(AdvisorKnowledgeLink(advisor_id=advisor_dist.id, knowledge_base_id=kb_dist.id))

    existing_sec_kb = (await db.execute(select(KnowledgeBase).where(KnowledgeBase.domain_tag == "zero_trust_security"))).scalar_one_or_none()
    if not existing_sec_kb:
        kb_sec = KnowledgeBase(
            name="Zero-Trust Boundary Specifications",
            domain_tag="zero_trust_security",
            description="Security boundaries restricting Copilot and agent access strictly to typed APIs.",
            documents=[
                {
                    "title": "Owner Copilot Isolation Policy",
                    "content": "The Copilot has zero direct SQL or database access. It can only query typed endpoints validated by Pydantic models."
                }
            ]
        )
        db.add(kb_sec)
        await db.flush()

        advisor_sec = Advisor(
            name="Elena Rostova",
            domain="SECURITY_COMPLIANCE",
            reasoning_model="o3-mini",
            system_prompt="You are Elena Rostova, Senior Advisor on Zero-Trust Boundaries and Sandbox Integrity.",
            status="ACTIVE"
        )
        db.add(advisor_sec)
        await db.flush()
        db.add(AdvisorKnowledgeLink(advisor_id=advisor_sec.id, knowledge_base_id=kb_sec.id))

    # Create Sample Kanban Tasks representing all state machine states
    task_count_res = await db.execute(select(func.count(Task.id)))
    task_count = task_count_res.scalar() or 0

    if task_count == 0:
        now = utc_now()
        tasks_to_create = [
            Task(
                title="Verify Local Host Daemon 15s Heartbeat Ping",
                description="Establish WebSocket handshake with /ws/daemon/{daemon_id} and maintain 15-second heartbeat intervals.",
                project_tag="folks_core",
                team_id=team.id,
                assigned_agent_id=agent_forge.id,
                status="IN_PROGRESS",
                priority="HIGH",
                lock_owner_id="daemon-host-01",
                lock_acquired_at=now,
                lock_expires_at=now + timedelta(seconds=60),
                lock_ttl_seconds=60,
                correlation_id="corr-heartbeat-001"
            ),
            Task(
                title="Zero-Trust Copilot Boundary Verification",
                description="Audit all Copilot endpoints to ensure zero direct SQL execution and strict Pydantic payload validation.",
                project_tag="folks_core",
                team_id=team.id,
                assigned_agent_id=agent_nova.id,
                status="PAUSED_FOR_CONSULTATION",
                priority="URGENT",
                lock_owner_id=agent_nova.id,
                lock_suspended=True,
                lock_suspended_remaining_seconds=45,
                correlation_id="corr-audit-002"
            ),
            Task(
                title="Investigate OOM Crash on Heavy Build Worker",
                description="Daemon process crashed unexpectedly due to memory overflow. Lock was automatically reaped by background sweeper.",
                project_tag="folks_core",
                team_id=team.id,
                status="DEAD_LETTER_QUEUE",
                priority="CRITICAL",
                dlq_reason="Daemon heartbeat missed 4 consecutive intervals (60s TTL expired). Lock reaped by background sweeper.",
                retry_count=1,
                correlation_id="corr-reaped-oom-99"
            ),
            Task(
                title="Configure Live Telemetry WebSocket Streaming",
                description="Stream stdout and stderr chunks from local daemon directly into Cockpit UI via /ws/cockpit.",
                project_tag="folks_core",
                team_id=team.id,
                status="DONE",
                priority="MEDIUM",
                correlation_id="corr-telemetry-done"
            ),
            Task(
                title="Implement Consultant Protocol Auto-Rejection",
                description="Ensure agents holding active Kanban task locks automatically reject incoming War Room invitations.",
                project_tag="folks_core",
                team_id=team.id,
                status="BACKLOG",
                priority="MEDIUM",
                correlation_id="corr-protocol-005"
            )
        ]
        db.add_all(tasks_to_create)

        # Add sample audit log
        audit = AuditLog(
            correlation_id="corr-reaped-oom-99",
            task_id="seeded-task-dlq",
            daemon_id="daemon-host-worker-04",
            event_type="LOCK_EXPIRED_REAPED",
            level="ERROR",
            message="Sweeper detected expired lock on Task. Reaped to DEAD_LETTER_QUEUE.",
            payload={"reason": "Daemon crashed / heartbeats ceased"}
        )
        db.add(audit)

    await db.commit()

    return {
        "status": "success",
        "message": "Demo data successfully seeded for Folks Multi-Agent Orchestrator",
        "team": team.name,
        "agents": agent_names
    }
