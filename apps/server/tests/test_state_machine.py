import pytest
from packages.db_schema.models import Agent, Task
from app.core.state_machine import (
    OrchestratorStateMachine,
    ProjectTagMismatchError,
    AgentBusyError
)

@pytest.mark.asyncio
async def test_task_checkout_and_project_tag_boundary(db_session):
    agent = Agent(
        name="Backend Dev",
        role="Senior Engineer",
        project_tags=["proj_billing"]
    )
    db_session.add(agent)

    task_matching = Task(
        title="Implement Stripe Webhook",
        project_tag="proj_billing",
        status="QUEUED"
    )
    task_foreign = Task(
        title="Optimize Mobile Layout",
        project_tag="proj_frontend",
        status="QUEUED"
    )
    db_session.add_all([task_matching, task_foreign])
    await db_session.commit()

    checked_out = await OrchestratorStateMachine.checkout_task(
        db=db_session,
        agent_id=agent.id,
        task_id=task_matching.id,
        correlation_id="corr-checkout-1",
        lock_ttl_seconds=60
    )
    assert checked_out.status == "IN_PROGRESS"
    assert checked_out.assigned_agent_id == agent.id
    assert checked_out.lock_owner_id == agent.id
    assert checked_out.lock_expires_at is not None
    assert agent.status == "IN_PROGRESS"

    with pytest.raises(ProjectTagMismatchError):
        other_agent = Agent(name="Frontend Dev", role="Dev", project_tags=["proj_frontend"])
        db_session.add(other_agent)
        await db_session.commit()

        task_billing_2 = Task(title="Audit Invoices", project_tag="proj_billing", status="QUEUED")
        db_session.add(task_billing_2)
        await db_session.commit()

        await OrchestratorStateMachine.checkout_task(
            db=db_session,
            agent_id=other_agent.id,
            task_id=task_billing_2.id,
            correlation_id="corr-mismatch"
        )


@pytest.mark.asyncio
async def test_consultant_protocol_and_busy_rejection(db_session):
    agent_a = Agent(name="Agent A", role="Lead", project_tags=["proj_core"])
    agent_b = Agent(name="Agent B (Idle)", role="Specialist", project_tags=["proj_core"])
    agent_c = Agent(name="Agent C (Busy)", role="Specialist", project_tags=["proj_core"])
    db_session.add_all([agent_a, agent_b, agent_c])

    task_1 = Task(title="Task 1", project_tag="proj_core", status="QUEUED")
    task_2 = Task(title="Task 2", project_tag="proj_core", status="QUEUED")
    db_session.add_all([task_1, task_2])
    await db_session.commit()

    await OrchestratorStateMachine.checkout_task(
        db=db_session,
        agent_id=agent_a.id,
        task_id=task_1.id,
        correlation_id="corr-task-1"
    )

    await OrchestratorStateMachine.checkout_task(
        db=db_session,
        agent_id=agent_c.id,
        task_id=task_2.id,
        correlation_id="corr-task-2"
    )

    assert agent_a.status == "IN_PROGRESS"
    assert agent_b.status == "IDLE"
    assert agent_c.status == "IN_PROGRESS"

    war_room, accepted, rejected = await OrchestratorStateMachine.create_war_room_and_invite(
        db=db_session,
        initiator_agent_id=agent_a.id,
        task_id=task_1.id,
        title="Database Migration Deadlock Debate",
        invitee_agent_ids=[agent_b.id, agent_c.id],
        correlation_id="corr-war-room"
    )

    assert agent_b.id in accepted
    assert agent_b.status == "CONSULTANT_ACTIVE"

    assert agent_c.id in rejected
    assert agent_c.status == "IN_PROGRESS"

    await OrchestratorStateMachine.conclude_war_room(
        db=db_session,
        war_room_id=war_room.id,
        correlation_id="corr-conclude"
    )
    assert agent_b.status == "IDLE"
    assert war_room.status == "CONCLUDED"


@pytest.mark.asyncio
async def test_lock_suspension_and_resume(db_session):
    agent = Agent(name="Dev", role="Lead", project_tags=["proj_api"])
    task = Task(title="Build Endpoint", project_tag="proj_api", status="QUEUED")
    db_session.add_all([agent, task])
    await db_session.commit()

    await OrchestratorStateMachine.checkout_task(
        db=db_session,
        agent_id=agent.id,
        task_id=task.id,
        correlation_id="corr-suspend-test",
        lock_ttl_seconds=60
    )
    assert task.status == "IN_PROGRESS"
    assert task.lock_suspended is False

    suspended_task = await OrchestratorStateMachine.suspend_task_for_consultation(
        db=db_session,
        task_id=task.id,
        correlation_id="corr-suspend-call"
    )
    assert suspended_task.status == "PAUSED_FOR_CONSULTATION"
    assert suspended_task.lock_suspended is True
    assert suspended_task.lock_suspended_remaining_seconds is not None
    assert suspended_task.lock_suspended_remaining_seconds >= 10
    assert agent.status == "PAUSED_FOR_CONSULTATION"

    resumed_task = await OrchestratorStateMachine.resume_task_from_consultation(
        db=db_session,
        task_id=task.id,
        correlation_id="corr-resume-call"
    )
    assert resumed_task.status == "IN_PROGRESS"
    assert resumed_task.lock_suspended is False
    assert resumed_task.lock_expires_at is not None
    assert agent.status == "IN_PROGRESS"
