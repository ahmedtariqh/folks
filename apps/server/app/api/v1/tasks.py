from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.db.session import get_db
from packages.db_schema.models import Task, AuditLog
from app.schemas.entities import (
    TaskCreate,
    TaskRead,
    TaskCheckoutRequest,
    TaskSuspendRequest,
    TaskResumeRequest
)
from app.core.state_machine import (
    OrchestratorStateMachine,
    StateMachineError,
    AgentBusyError,
    ProjectTagMismatchError,
    TaskLockConflictError,
    InvalidStateTransitionError
)

router = APIRouter(prefix="/tasks", tags=["Kanban & Task Lifecycle"])

@router.post("", response_model=TaskRead)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(
        title=payload.title,
        description=payload.description,
        project_tag=payload.project_tag,
        priority=payload.priority,
        team_id=payload.team_id,
        status="BACKLOG"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get("", response_model=List[TaskRead])
async def list_tasks(
    project_tag: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task)
    if project_tag:
        stmt = stmt.where(Task.project_tag == project_tag)
    if status:
        stmt = stmt.where(Task.status == status)
    if team_id:
        stmt = stmt.where(Task.team_id == team_id)

    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/dlq", response_model=List[TaskRead])
async def list_dlq_tasks(db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.status == "DEAD_LETTER_QUEUE")
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{task_id}/checkout", response_model=TaskRead)
async def checkout_task(
    task_id: str,
    payload: TaskCheckoutRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        task = await OrchestratorStateMachine.checkout_task(
            db=db,
            agent_id=payload.agent_id,
            task_id=task_id,
            correlation_id=payload.correlation_id,
            daemon_id=payload.daemon_id,
            lock_ttl_seconds=payload.lock_ttl_seconds
        )
        await db.commit()
        await db.refresh(task)
        return task
    except AgentBusyError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ProjectTagMismatchError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TaskLockConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except StateMachineError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{task_id}/suspend", response_model=TaskRead)
async def suspend_task(
    task_id: str,
    payload: TaskSuspendRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        task = await OrchestratorStateMachine.suspend_task_for_consultation(
            db=db,
            task_id=task_id,
            correlation_id=payload.correlation_id
        )
        await db.commit()
        await db.refresh(task)
        return task
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StateMachineError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{task_id}/resume", response_model=TaskRead)
async def resume_task(
    task_id: str,
    payload: TaskResumeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        task = await OrchestratorStateMachine.resume_task_from_consultation(
            db=db,
            task_id=task_id,
            correlation_id=payload.correlation_id
        )
        await db.commit()
        await db.refresh(task)
        return task
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StateMachineError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{task_id}/block", response_model=TaskRead)
async def block_task(
    task_id: str,
    reason: str = Query(...),
    correlation_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(Task.id == task_id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "BLOCKED"
    task.blocker_reason = reason
    audit = AuditLog(
        correlation_id=correlation_id,
        agent_id=task.assigned_agent_id,
        task_id=task.id,
        event_type="ROADBLOCK_ESCALATED",
        level="WARN",
        message=f"Agent escalated blocker on Task {task.id}: {reason}",
        payload={"reason": reason}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(task)
    return task
