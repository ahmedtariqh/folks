import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from packages.db_schema.models import Task, Agent, AuditLog, utc_now
from app.db.session import AsyncSessionLocal
from app.core.config import settings

logger = logging.getLogger("folks.reaper")

class LockReaper:
    """
    Infrastructure Resilience & Daemon Failure Recovery:
    1. Lock renewal via daemon heartbeats (15s cadence, 60s TTL).
    2. Sweeper detecting expired locks and reaping them into the Dead-Letter Queue (DLQ).
    3. Tracing with unified Correlation IDs.
    """

    @staticmethod
    async def renew_heartbeat(
        db: AsyncSession,
        task_id: str,
        daemon_id: str,
        correlation_id: str,
        ttl_seconds: int = 60
    ) -> bool:
        task_stmt = select(Task).where(Task.id == task_id)
        task_res = await db.execute(task_stmt)
        task = task_res.scalar_one_or_none()
        if not task:
            logger.warning(f"[corr_id: {correlation_id}] Heartbeat rejected: Task {task_id} not found.")
            return False

        if task.status != "IN_PROGRESS" or task.lock_suspended:
            logger.warning(
                f"[corr_id: {correlation_id}] Heartbeat ignored: Task {task_id} in status '{task.status}', suspended={task.lock_suspended}."
            )
            return False

        now = utc_now()
        task.lock_expires_at = now + timedelta(seconds=ttl_seconds)
        task.lock_owner_id = daemon_id

        audit = AuditLog(
            correlation_id=correlation_id,
            agent_id=task.assigned_agent_id,
            task_id=task.id,
            daemon_id=daemon_id,
            event_type="LOCK_RENEWED",
            level="DEBUG",
            message=f"Lock renewed for Task {task.id} by Daemon {daemon_id}. New expiry: {task.lock_expires_at.isoformat()}",
            payload={"expires_at": task.lock_expires_at.isoformat(), "ttl_seconds": ttl_seconds}
        )
        db.add(audit)
        await db.flush()
        return True

    @staticmethod
    async def sweep_expired_locks(db: AsyncSession) -> List[str]:
        now = utc_now()
        stmt = select(Task).where(
            and_(
                Task.status == "IN_PROGRESS",
                Task.lock_suspended == False,
                Task.lock_expires_at.is_not(None),
                Task.lock_expires_at < now
            )
        )
        res = await db.execute(stmt)
        expired_tasks = res.scalars().all()

        reaped_task_ids = []
        for task in expired_tasks:
            corr_id = task.correlation_id or "system-reaper"
            logger.error(
                f"[corr_id: {corr_id}] REAPING EXPIRED LOCK on Task {task.id}. "
                f"Expired at {task.lock_expires_at}, now is {now}. Moving to DLQ."
            )

            task.status = "DEAD_LETTER_QUEUE"
            task.dlq_reason = f"DAEMON_HEARTBEAT_TIMEOUT: Lock expired at {task.lock_expires_at.isoformat()} without renewal (>60s). Daemon assumed crashed or disconnected."
            task.lock_owner_id = None
            task.lock_expires_at = None
            task.retry_count += 1
            reaped_task_ids.append(task.id)

            if task.assigned_agent_id:
                agent_stmt = select(Agent).where(Agent.id == task.assigned_agent_id)
                agent_res = await db.execute(agent_stmt)
                agent = agent_res.scalar_one_or_none()
                if agent and agent.status == "IN_PROGRESS":
                    agent.status = "IDLE"

            audit = AuditLog(
                correlation_id=corr_id,
                agent_id=task.assigned_agent_id,
                task_id=task.id,
                event_type="DLQ_REAPED",
                level="ERROR",
                message=f"Lock expired for Task {task.id}. Daemon missed heartbeats. Routed to Dead-Letter Queue.",
                payload={"dlq_reason": task.dlq_reason, "retry_count": task.retry_count}
            )
            db.add(audit)

        if reaped_task_ids:
            await db.flush()

        return reaped_task_ids


async def run_lock_sweeper_loop():
    logger.info("Starting Folks Lock Sweeper daemon loop...")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                reaped = await LockReaper.sweep_expired_locks(db)
                if reaped:
                    await db.commit()
                    logger.info(f"Sweeper reaped {len(reaped)} expired tasks to DLQ: {reaped}")
        except Exception as e:
            logger.error(f"Error in lock sweeper loop: {e}", exc_info=True)
        await asyncio.sleep(settings.LOCK_SWEEPER_INTERVAL_SECONDS)
