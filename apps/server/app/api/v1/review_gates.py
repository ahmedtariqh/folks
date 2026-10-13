from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from packages.db_schema.models import ReviewGate, Task, Agent, AuditLog, utc_now
from app.schemas.entities import ReviewGateCreate, ReviewGateRead, ReviewGateActionRequest

router = APIRouter(prefix="/review-gates", tags=["Review Gates & Human Validation"])

@router.post("", response_model=ReviewGateRead)
async def submit_for_review(payload: ReviewGateCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id == payload.task_id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    gate = ReviewGate(
        task_id=payload.task_id,
        agent_id=payload.agent_id,
        diff_patch=payload.diff_patch,
        test_results=payload.test_results,
        status="PENDING",
        correlation_id=payload.correlation_id
    )
    db.add(gate)

    task.status = "AWAITING_REVIEW"

    corr_id = payload.correlation_id or "review-submit"
    audit = AuditLog(
        correlation_id=corr_id,
        agent_id=payload.agent_id,
        task_id=payload.task_id,
        event_type="SUBMITTED_FOR_REVIEW",
        level="INFO",
        message=f"Agent {payload.agent_id} submitted Task {payload.task_id} diff to Review Gate.",
        payload={"diff_length": len(payload.diff_patch)}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(gate)
    return gate

@router.get("", response_model=List[ReviewGateRead])
async def list_pending_reviews(status: str = "PENDING", db: AsyncSession = Depends(get_db)):
    stmt = select(ReviewGate)
    if status:
        stmt = stmt.where(ReviewGate.status == status)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{gate_id}", response_model=ReviewGateRead)
async def get_review_gate(gate_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ReviewGate).where(ReviewGate.id == gate_id)
    res = await db.execute(stmt)
    gate = res.scalar_one_or_none()
    if not gate:
        raise HTTPException(status_code=404, detail="Review Gate entry not found")
    return gate

@router.post("/{gate_id}/action", response_model=ReviewGateRead)
async def act_on_review(
    gate_id: str,
    payload: ReviewGateActionRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ReviewGate).where(ReviewGate.id == gate_id)
    res = await db.execute(stmt)
    gate = res.scalar_one_or_none()
    if not gate:
        raise HTTPException(status_code=404, detail="Review Gate entry not found")

    task_stmt = select(Task).where(Task.id == gate.task_id)
    task_res = await db.execute(task_stmt)
    task = task_res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Associated task not found")

    gate.owner_feedback = payload.feedback
    gate.reviewed_at = utc_now()
    corr_id = gate.correlation_id or "human-review"

    if payload.action == "APPROVE":
        gate.status = "APPROVED"
        task.status = "DONE"
        task.lock_owner_id = None
        task.lock_expires_at = None

        if task.assigned_agent_id:
            ag_stmt = select(Agent).where(Agent.id == task.assigned_agent_id)
            ag_res = await db.execute(ag_stmt)
            agent = ag_res.scalar_one_or_none()
            if agent:
                agent.status = "IDLE"

        audit = AuditLog(
            correlation_id=corr_id,
            agent_id=task.assigned_agent_id,
            task_id=task.id,
            event_type="REVIEW_APPROVED",
            level="INFO",
            message=f"Owner APPROVED Task {task.id}. Task completed and merged.",
            payload={"feedback": payload.feedback}
        )
        db.add(audit)

    else:
        gate.status = "REJECTED"
        task.status = "IN_PROGRESS"

        audit = AuditLog(
            correlation_id=corr_id,
            agent_id=task.assigned_agent_id,
            task_id=task.id,
            event_type="REVIEW_REJECTED",
            level="WARN",
            message=f"Owner REJECTED Task {task.id}. Changes requested.",
            payload={"feedback": payload.feedback}
        )
        db.add(audit)

    await db.commit()
    await db.refresh(gate)
    return gate
