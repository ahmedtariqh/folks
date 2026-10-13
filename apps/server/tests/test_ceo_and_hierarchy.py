import sys
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from packages.db_schema.models import Agent, Team, TeamMembership, Task, Advisor, AgentMessage, AuditLog
from app.core.ceo_engine import CEOEngine
from app.main import app
from app.db.session import get_db

@pytest.mark.asyncio
async def test_ceo_engine_reporting_and_delegation(db_session):
    # 1. Setup CEO agent and team
    ceo = Agent(
        name="Nova - Lead Orchestrator",
        role="Chief Executive Agent",
        status="IDLE",
        model_name="gpt-4o",
        project_tags=["apex_core"]
    )
    db_session.add(ceo)
    await db_session.flush()

    team = Team(
        name="Apex Core",
        project_tag="apex_core",
        mission="Autonomous orchestration",
        lead_agent_id=ceo.id
    )
    db_session.add(team)
    await db_session.flush()

    membership = TeamMembership(team_id=team.id, agent_id=ceo.id, team_role="Lead")
    db_session.add(membership)
    await db_session.commit()

    # 2. Test status reporting
    report_res = await CEOEngine.process_ceo_directive(
        db=db_session,
        user_message="Please generate an executive status report for our squad",
        project_tag="apex_core"
    )
    assert report_res["intent"] == "STATUS_REPORT"
    assert "Nova - Lead Orchestrator" in report_res["ceo_name"]
    assert "report_data" in report_res
    assert report_res["report_data"]["tasks_count"]["total"] == 0

    # 3. Test task delegation
    delegate_msg = 'Delegate task: "Implement Daemon Heartbeat Verifier" to Nova [HIGH]: Verify 15s ping intervals.'
    delegate_res = await CEOEngine.process_ceo_directive(
        db=db_session,
        user_message=delegate_msg,
        project_tag="apex_core"
    )
    assert delegate_res["intent"] == "TASK_DELEGATION"
    assert len(delegate_res["actions_taken"]) == 1
    action = delegate_res["actions_taken"][0]
    assert action["title"] == "Implement Daemon Heartbeat Verifier"
    assert action["priority"] == "HIGH"
    assert action["assigned_agent_name"] == "Nova - Lead Orchestrator"

    # Verify task was created in DB
    from sqlalchemy import select
    task_res = await db_session.execute(select(Task).where(Task.title == "Implement Daemon Heartbeat Verifier"))
    created_task = task_res.scalar_one_or_none()
    assert created_task is not None
    assert created_task.assigned_agent_id == ceo.id
    assert created_task.priority == "HIGH"
    assert created_task.status in ["BACKLOG", "QUEUED"]

    # Verify audit log was recorded
    audit_res = await db_session.execute(select(AuditLog).where(AuditLog.event_type == "CEO_DELEGATION"))
    audit_entry = audit_res.scalar_one_or_none()
    assert audit_entry is not None

@pytest.mark.asyncio
async def test_team_hierarchy_and_agent_dialogue_api(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup CEO, specialist agent, team, and advisor
        ceo = Agent(name="Nova - CEO", role="Chief Executive", status="IDLE", project_tags=["core"])
        worker = Agent(name="Dev - Backend", role="Backend Engineer", status="IDLE", project_tags=["core"])
        advisor = Advisor(
            name="Dr. Turing",
            domain="Distributed Systems",
            reasoning_model="deepseek-r1",
            system_prompt="Analyze distributed systems invariants and lock guarantees.",
            status="ACTIVE"
        )
        db_session.add_all([ceo, worker, advisor])
        await db_session.flush()

        team = Team(name="Engineering Squad", project_tag="core", mission="Build systems", lead_agent_id=ceo.id)
        db_session.add(team)
        await db_session.flush()

        db_session.add(TeamMembership(team_id=team.id, agent_id=ceo.id, team_role="Lead"))
        db_session.add(TeamMembership(team_id=team.id, agent_id=worker.id, team_role="Specialist"))
        await db_session.commit()

        # 2. Test Hierarchy endpoint
        hier_res = await client.get("/api/v1/teams/hierarchy")
        assert hier_res.status_code == 200
        data = hier_res.json()
        assert data["ceo"]["name"] == "Nova - CEO"
        assert len(data["advisors"]) == 1
        assert data["advisors"][0]["name"] == "Dr. Turing"
        assert len(data["teams"]) == 1
        assert len(data["teams"][0]["members"]) == 2

        # 3. Test Direct 1-on-1 Agent Dialogue
        chat_res = await client.post(
            f"/api/v1/agents/{worker.id}/chat",
            json={"message": "What is your current status and what are you working on?"}
        )
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        assert chat_data["agent_name"] == "Dev - Backend"
        assert "IDLE" in chat_data["response"]

        # 4. Test Agent Message History
        history_res = await client.get(f"/api/v1/agents/{worker.id}/messages")
        assert history_res.status_code == 200
        messages = history_res.json()
        assert len(messages) == 2
        assert messages[0]["sender_type"] == "USER"
        assert messages[1]["sender_type"] == "AGENT"

        # 5. Test CEO Chat via API
        ceo_chat_res = await client.post(
            "/api/v1/ceo/chat",
            json={"message": "Summarize organizational status"}
        )
        assert ceo_chat_res.status_code == 200
        assert ceo_chat_res.json()["intent"] == "STATUS_REPORT"

    app.dependency_overrides.clear()
