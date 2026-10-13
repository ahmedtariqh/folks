import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from packages.db_schema.models import Agent, Task, AuditLog, utc_now
from app.core.reaper import LockReaper
from app.core.state_machine import OrchestratorStateMachine

@pytest.mark.asyncio
async def test_daemon_heartbeat_renewal(db_session):
    agent = Agent(name="Runner Agent", role="Worker", project_tags=["proj_ops"])
    task = Task(title="Deploy Release", project_tag="proj_ops", status="QUEUED")
    db_session.add_all([agent, task])
    await db_session.commit()

    await OrchestratorStateMachine.checkout_task(
        db=db_session,
        agent_id=agent.id,
        task_id=task.id,
        correlation_id="corr-hb-test",
        daemon_id="daemon-host-01",
        lock_ttl_seconds=60
    )

    initial_expiry = task.lock_expires_at
    assert initial_expiry is not None

    renewed = await LockReaper.renew_heartbeat(
        db=db_session,
        task_id=task.id,
        daemon_id="daemon-host-01",
        correlation_id="corr-hb-test",
        ttl_seconds=60
    )
    assert renewed is True
    assert task.lock_expires_at >= initial_expiry


@pytest.mark.asyncio
async def test_daemon_failure_automatic_reaping_to_dlq(db_session):
    corr_id = "corr-crash-simulation-99"
    agent = Agent(name="Crashed Worker", role="Worker", project_tags=["proj_cloud"], status="IN_PROGRESS")
    
    expired_time = utc_now() - timedelta(seconds=10)
    task = Task(
        title="Heavy ML Training Job",
        project_tag="proj_cloud",
        status="IN_PROGRESS",
        assigned_agent_id=agent.id,
        lock_owner_id="daemon-crashed-x",
        lock_expires_at=expired_time,
        lock_suspended=False,
        correlation_id=corr_id
    )
    db_session.add_all([agent, task])
    await db_session.commit()

    reaped_ids = await LockReaper.sweep_expired_locks(db_session)
    await db_session.commit()
    await db_session.refresh(agent)

    assert task.id in reaped_ids
    assert task.status == "DEAD_LETTER_QUEUE"
    assert "DAEMON_HEARTBEAT_TIMEOUT" in task.dlq_reason
    assert task.lock_owner_id is None
    assert task.retry_count == 1
    assert agent.status == "IDLE"

    audit_stmt = select(AuditLog).where(
        AuditLog.correlation_id == corr_id,
        AuditLog.event_type == "DLQ_REAPED"
    )
    audit_res = await db_session.execute(audit_stmt)
    reap_audit = audit_res.scalar_one_or_none()
    assert reap_audit is not None
    assert reap_audit.level == "ERROR"


@pytest.mark.asyncio
async def test_suspended_locks_protected_from_reaper(db_session):
    agent = Agent(name="Consulting Dev", role="Architect", project_tags=["proj_sec"], status="PAUSED_FOR_CONSULTATION")
    past_time = utc_now() - timedelta(minutes=5)
    
    task_suspended = Task(
        title="Security Audit Roadblock",
        project_tag="proj_sec",
        status="PAUSED_FOR_CONSULTATION",
        assigned_agent_id=agent.id,
        lock_owner_id="daemon-01",
        lock_expires_at=past_time,
        lock_suspended=True,
        lock_suspended_remaining_seconds=45,
        correlation_id="corr-protect-test"
    )
    db_session.add_all([agent, task_suspended])
    await db_session.commit()

    reaped_ids = await LockReaper.sweep_expired_locks(db_session)
    await db_session.commit()

    assert task_suspended.id not in reaped_ids
    assert task_suspended.status == "PAUSED_FOR_CONSULTATION"
    assert task_suspended.lock_suspended is True
