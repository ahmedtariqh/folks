from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from packages.db_schema.models import Agent, Task, WarRoom, WarRoomParticipant, WarRoomMessage, ReviewGate, AuditLog, utc_now

class StateMachineError(Exception):
    """Base class for state machine violations."""
    pass

class AgentBusyError(StateMachineError):
    """Raised when an invitee is busy with another locked task."""
    pass

class ProjectTagMismatchError(StateMachineError):
    """Raised when agent project tags do not permit checking out a task."""
    pass

class TaskLockConflictError(StateMachineError):
    """Raised when a task is already locked or not in a checkable status."""
    pass

class InvalidStateTransitionError(StateMachineError):
    """Raised when an illegal status change is attempted."""
    pass


class OrchestratorStateMachine:
    """
    Core state machine enforcing:
    1. Kanban is primary, War Rooms are sub-routines.
    2. Consultant Protocol (Agent B joins as ephemeral Consultant without checking out tasks).
    3. Lock Suspension (Task shifts to PAUSED_FOR_CONSULTATION, TTL is frozen).
    4. Busy Rejection (Agents executing tasks automatically reject War Room invites).
    5. Project Tag authorization boundary.
    """

    @staticmethod
    async def checkout_task(
        db: AsyncSession,
        agent_id: str,
        task_id: str,
        correlation_id: str,
        daemon_id: Optional[str] = None,
        lock_ttl_seconds: int = 60
    ) -> Task:
        # 1. Verify Agent availability
        agent_stmt = select(Agent).where(Agent.id == agent_id)
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if not agent:
            raise StateMachineError(f"Agent {agent_id} not found.")

        if agent.status not in ("IDLE",):
            raise AgentBusyError(
                f"Agent {agent.name} ({agent.id}) cannot checkout task: currently in status '{agent.status}'."
            )

        # 2. Query task
        task_stmt = select(Task).where(Task.id == task_id)
        task_res = await db.execute(task_stmt)
        task = task_res.scalar_one_or_none()
        if not task:
            raise StateMachineError(f"Task {task_id} not found.")

        if task.status not in ("BACKLOG", "QUEUED"):
            raise TaskLockConflictError(
                f"Task {task_id} is in status '{task.status}', cannot be checked out."
            )

        # 3. Verify Project Tag authorization
        agent_tags = agent.project_tags or []
        if task.project_tag not in agent_tags:
            raise ProjectTagMismatchError(
                f"Security Boundary Violation: Agent project tags {agent_tags} do not contain required project tag '{task.project_tag}'."
            )

        # 4. Acquire Lock
        now = utc_now()
        expires_at = now + timedelta(seconds=lock_ttl_seconds)

        task.status = "IN_PROGRESS"
        task.assigned_agent_id = agent.id
        task.lock_owner_id = daemon_id or agent.id
        task.lock_acquired_at = now
        task.lock_expires_at = expires_at
        task.lock_ttl_seconds = lock_ttl_seconds
        task.lock_suspended = False
        task.lock_suspended_remaining_seconds = None
        task.correlation_id = correlation_id
        task.dlq_reason = None

        agent.status = "IN_PROGRESS"

        audit = AuditLog(
            correlation_id=correlation_id,
            agent_id=agent.id,
            task_id=task.id,
            daemon_id=daemon_id,
            event_type="LOCK_ACQUIRED",
            level="INFO",
            message=f"Agent {agent.name} checked out Task {task.id} with {lock_ttl_seconds}s TTL",
            payload={"expires_at": expires_at.isoformat(), "project_tag": task.project_tag}
        )
        db.add(audit)
        await db.flush()
        return task

    @staticmethod
    async def create_war_room_and_invite(
        db: AsyncSession,
        initiator_agent_id: str,
        task_id: str,
        title: str,
        invitee_agent_ids: List[str],
        correlation_id: str
    ) -> Tuple[WarRoom, List[str], List[str]]:
        task_stmt = select(Task).where(Task.id == task_id)
        task_res = await db.execute(task_stmt)
        task = task_res.scalar_one_or_none()
        if not task:
            raise StateMachineError(f"Task {task_id} not found.")

        if task.assigned_agent_id != initiator_agent_id or task.status not in ("IN_PROGRESS", "PAUSED_FOR_CONSULTATION"):
            raise StateMachineError(
                f"Agent {initiator_agent_id} does not hold active lock for Task {task_id} (status: {task.status})."
            )

        war_room = WarRoom(
            task_id=task.id,
            title=title,
            initiator_agent_id=initiator_agent_id,
            status="ACTIVE"
        )
        db.add(war_room)
        await db.flush()

        init_part = WarRoomParticipant(
            war_room_id=war_room.id,
            agent_id=initiator_agent_id,
            role="INITIATOR"
        )
        db.add(init_part)

        accepted_ids = [initiator_agent_id]
        rejected_ids = []

        for invitee_id in invitee_agent_ids:
            if invitee_id == initiator_agent_id:
                continue

            agent_stmt = select(Agent).where(Agent.id == invitee_id)
            agent_res = await db.execute(agent_stmt)
            invitee = agent_res.scalar_one_or_none()
            if not invitee:
                rejected_ids.append(invitee_id)
                continue

            if invitee.status != "IDLE":
                rejected_ids.append(invitee_id)
                audit = AuditLog(
                    correlation_id=correlation_id,
                    agent_id=invitee.id,
                    task_id=task.id,
                    event_type="WAR_ROOM_INVITE_REJECTED",
                    level="WARN",
                    message=f"Agent {invitee.name} automatically rejected War Room invite: status is '{invitee.status}' (Busy Rejection).",
                    payload={"war_room_id": war_room.id}
                )
                db.add(audit)
                continue

            invitee.status = "CONSULTANT_ACTIVE"
            consultant_part = WarRoomParticipant(
                war_room_id=war_room.id,
                agent_id=invitee.id,
                role="CONSULTANT"
            )
            db.add(consultant_part)
            accepted_ids.append(invitee.id)

            audit = AuditLog(
                correlation_id=correlation_id,
                agent_id=invitee.id,
                task_id=task.id,
                event_type="WAR_ROOM_JOINED_CONSULTANT",
                level="INFO",
                message=f"Agent {invitee.name} joined War Room '{title}' as ephemeral Consultant.",
                payload={"war_room_id": war_room.id}
            )
            db.add(audit)

        await db.flush()
        return war_room, accepted_ids, rejected_ids

    @staticmethod
    async def suspend_task_for_consultation(
        db: AsyncSession,
        task_id: str,
        correlation_id: str
    ) -> Task:
        task_stmt = select(Task).where(Task.id == task_id)
        task_res = await db.execute(task_stmt)
        task = task_res.scalar_one_or_none()
        if not task:
            raise StateMachineError(f"Task {task_id} not found.")

        if task.status != "IN_PROGRESS":
            raise InvalidStateTransitionError(
                f"Cannot suspend task in status '{task.status}'. Must be 'IN_PROGRESS'."
            )

        now = utc_now()
        remaining_seconds = 0
        if task.lock_expires_at:
            delta = (task.lock_expires_at - now).total_seconds()
            remaining_seconds = max(10, int(delta))
        else:
            remaining_seconds = task.lock_ttl_seconds

        task.status = "PAUSED_FOR_CONSULTATION"
        task.lock_suspended = True
        task.lock_suspended_remaining_seconds = remaining_seconds

        if task.assigned_agent_id:
            agent_stmt = select(Agent).where(Agent.id == task.assigned_agent_id)
            agent_res = await db.execute(agent_stmt)
            agent = agent_res.scalar_one_or_none()
            if agent:
                agent.status = "PAUSED_FOR_CONSULTATION"

        audit = AuditLog(
            correlation_id=correlation_id,
            agent_id=task.assigned_agent_id,
            task_id=task.id,
            event_type="LOCK_SUSPENDED",
            level="INFO",
            message=f"Task {task.id} lock suspended for consultation. {remaining_seconds}s TTL frozen.",
            payload={"remaining_seconds": remaining_seconds}
        )
        db.add(audit)
        await db.flush()
        return task

    @staticmethod
    async def resume_task_from_consultation(
        db: AsyncSession,
        task_id: str,
        correlation_id: str
    ) -> Task:
        task_stmt = select(Task).where(Task.id == task_id)
        task_res = await db.execute(task_stmt)
        task = task_res.scalar_one_or_none()
        if not task:
            raise StateMachineError(f"Task {task_id} not found.")

        if task.status != "PAUSED_FOR_CONSULTATION":
            raise InvalidStateTransitionError(
                f"Cannot resume task in status '{task.status}'. Must be 'PAUSED_FOR_CONSULTATION'."
            )

        ttl = task.lock_suspended_remaining_seconds or task.lock_ttl_seconds or 60
        now = utc_now()
        task.status = "IN_PROGRESS"
        task.lock_suspended = False
        task.lock_suspended_remaining_seconds = None
        task.lock_expires_at = now + timedelta(seconds=ttl)

        if task.assigned_agent_id:
            agent_stmt = select(Agent).where(Agent.id == task.assigned_agent_id)
            agent_res = await db.execute(agent_stmt)
            agent = agent_res.scalar_one_or_none()
            if agent:
                agent.status = "IN_PROGRESS"

        audit = AuditLog(
            correlation_id=correlation_id,
            agent_id=task.assigned_agent_id,
            task_id=task.id,
            event_type="LOCK_RESUMED",
            level="INFO",
            message=f"Task {task.id} resumed from consultation. Lock refreshed with {ttl}s TTL.",
            payload={"expires_at": task.lock_expires_at.isoformat()}
        )
        db.add(audit)
        await db.flush()
        return task

    @staticmethod
    async def conclude_war_room(
        db: AsyncSession,
        war_room_id: str,
        correlation_id: str
    ) -> WarRoom:
        wr_stmt = select(WarRoom).where(WarRoom.id == war_room_id)
        wr_res = await db.execute(wr_stmt)
        war_room = wr_res.scalar_one_or_none()
        if not war_room:
            raise StateMachineError(f"War Room {war_room_id} not found.")

        war_room.status = "CONCLUDED"
        war_room.concluded_at = utc_now()

        part_stmt = select(WarRoomParticipant).where(WarRoomParticipant.war_room_id == war_room_id)
        part_res = await db.execute(part_stmt)
        participants = part_res.scalars().all()

        for p in participants:
            if p.role == "CONSULTANT":
                ag_stmt = select(Agent).where(Agent.id == p.agent_id)
                ag_res = await db.execute(ag_stmt)
                agent = ag_res.scalar_one_or_none()
                if agent and agent.status == "CONSULTANT_ACTIVE":
                    agent.status = "IDLE"

        audit = AuditLog(
            correlation_id=correlation_id,
            task_id=war_room.task_id,
            event_type="WAR_ROOM_CONCLUDED",
            level="INFO",
            message=f"War Room {war_room_id} concluded. All consultants released back to IDLE.",
            payload={"participant_count": len(participants)}
        )
        db.add(audit)
        await db.flush()
        return war_room
