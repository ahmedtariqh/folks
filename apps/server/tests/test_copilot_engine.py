import pytest
from packages.db_schema.models import Agent, Task, AuditLog
from app.core.copilot_engine import OwnerCopilotEngine
from app.schemas.copilot import (
    UpdateAgentBudgetRequest,
    AssignProjectTagRequest,
    RetryDLQTaskRequest
)

def test_copilot_ui_navigation_rag():
    results_budget = OwnerCopilotEngine.navigate_ui("I need to change the token budget limit")
    assert len(results_budget) > 0
    top = results_budget[0]
    assert top.route_path == "/settings/agents"
    assert "Budget" in top.screen_name
    assert top.action_available == "update_agent_budget"

    results_dlq = OwnerCopilotEngine.navigate_ui("Where are reaped tasks that crashed?")
    assert len(results_dlq) > 0
    assert results_dlq[0].route_path == "/kanban/dlq"

    results_war_room = OwnerCopilotEngine.navigate_ui("Show me active war room channels")
    assert results_war_room[0].route_path == "/war-rooms"


@pytest.mark.asyncio
async def test_copilot_diagnostic_trace_interpreter(db_session):
    corr_id = "corr-test-oom-failure"

    log1 = AuditLog(
        correlation_id=corr_id,
        task_id="task-123",
        daemon_id="daemon-host-01",
        event_type="LOCK_ACQUIRED",
        level="INFO",
        message="Lock acquired with 60s TTL"
    )
    log2 = AuditLog(
        correlation_id=corr_id,
        task_id="task-123",
        daemon_id="daemon-host-01",
        event_type="LOCK_RENEWED",
        level="DEBUG",
        message="Heartbeat received at 15s mark"
    )
    log3 = AuditLog(
        correlation_id=corr_id,
        task_id="task-123",
        daemon_id="daemon-host-01",
        event_type="DLQ_REAPED",
        level="ERROR",
        message="Lock expired without renewal. Routed to Dead-Letter Queue.",
        payload={"dlq_reason": "DAEMON_HEARTBEAT_TIMEOUT"}
    )
    db_session.add_all([log1, log2, log3])
    await db_session.commit()

    explanation = await OwnerCopilotEngine.explain_trace(db_session, corr_id)

    assert explanation.correlation_id == corr_id
    assert explanation.total_events == 3
    assert explanation.has_errors is True
    assert "Daemon Heartbeat Failure" in explanation.root_cause_summary
    assert "Dead-Letter Queue" in explanation.root_cause_summary
    assert "Restart the local daemon" in explanation.suggested_remedy


@pytest.mark.asyncio
async def test_copilot_typed_actions_zero_sql(db_session):
    agent = Agent(name="Dev Agent", role="Worker", monthly_budget_usd=30.0, project_tags=["proj_alpha"])
    task = Task(title="Failed Task", project_tag="proj_alpha", status="DEAD_LETTER_QUEUE", dlq_reason="OOM")
    db_session.add_all([agent, task])
    await db_session.commit()

    budget_req = UpdateAgentBudgetRequest(agent_id=agent.id, monthly_budget_usd=150.0)
    res_budget = await OwnerCopilotEngine.update_agent_budget(db_session, budget_req)
    assert res_budget.success is True
    assert agent.monthly_budget_usd == 150.0

    tag_req = AssignProjectTagRequest(agent_id=agent.id, project_tag="proj_beta")
    res_tag = await OwnerCopilotEngine.assign_project_tag(db_session, tag_req)
    assert res_tag.success is True
    assert "proj_beta" in agent.project_tags

    retry_req = RetryDLQTaskRequest(task_id=task.id, comment="Daemon restarted with more RAM")
    res_retry = await OwnerCopilotEngine.retry_dlq_task(db_session, retry_req)
    assert res_retry.success is True
    assert task.status == "QUEUED"
    assert task.dlq_reason is None
