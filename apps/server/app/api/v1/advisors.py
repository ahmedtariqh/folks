from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.db.session import get_db
from packages.db_schema.models import KnowledgeBase, Advisor, AdvisorKnowledgeLink, AdvisorySession
from app.schemas.advisory import (
    KnowledgeBaseCreate,
    KnowledgeBaseRead,
    AdvisorCreate,
    AdvisorRead,
    LinkKnowledgeBaseRequest,
    AdvisorySessionRequest,
    AdvisorySessionRead
)
from app.core.advisory_engine import AdvisoryEngine

router = APIRouter(prefix="/advisors", tags=["Board of Advisors & Knowledge Bases"])

# 1. Knowledge Bases
@router.post("/knowledge-bases", response_model=KnowledgeBaseRead)
async def create_knowledge_base(payload: KnowledgeBaseCreate, db: AsyncSession = Depends(get_db)):
    """Create a heavy-weight domain knowledge base (architecture standards, compliance, whitepapers)."""
    kb = KnowledgeBase(
        name=payload.name,
        description=payload.description,
        domain_tag=payload.domain_tag,
        documents=[doc.model_dump() for doc in payload.documents]
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return kb

@router.get("/knowledge-bases", response_model=List[KnowledgeBaseRead])
async def list_knowledge_bases(db: AsyncSession = Depends(get_db)):
    """List all registered knowledge bases."""
    stmt = select(KnowledgeBase)
    res = await db.execute(stmt)
    return res.scalars().all()

# 2. Board of Advisors
@router.post("", response_model=AdvisorRead)
async def create_advisor(payload: AdvisorCreate, db: AsyncSession = Depends(get_db)):
    """Appoint a new Advisor to the Board of Advisors with deep reasoning capabilities."""
    advisor = Advisor(
        name=payload.name,
        domain=payload.domain,
        reasoning_model=payload.reasoning_model,
        system_prompt=payload.system_prompt,
        status="ACTIVE"
    )
    db.add(advisor)
    await db.flush()

    for kb_id in payload.knowledge_base_ids:
        link = AdvisorKnowledgeLink(advisor_id=advisor.id, knowledge_base_id=kb_id)
        db.add(link)

    await db.commit()
    await db.refresh(advisor)

    return AdvisorRead(
        id=advisor.id,
        name=advisor.name,
        domain=advisor.domain,
        reasoning_model=advisor.reasoning_model,
        system_prompt=advisor.system_prompt,
        status=advisor.status,
        linked_knowledge_base_ids=payload.knowledge_base_ids,
        created_at=advisor.created_at
    )

@router.get("", response_model=List[AdvisorRead])
async def list_advisors(db: AsyncSession = Depends(get_db)):
    """List all advisors on the Board with their linked knowledge bases."""
    stmt = select(Advisor).options(selectinload(Advisor.knowledge_links))
    res = await db.execute(stmt)
    advisors = res.scalars().all()

    result = []
    for a in advisors:
        kb_ids = [link.knowledge_base_id for link in a.knowledge_links]
        result.append(
            AdvisorRead(
                id=a.id,
                name=a.name,
                domain=a.domain,
                reasoning_model=a.reasoning_model,
                system_prompt=a.system_prompt,
                status=a.status,
                linked_knowledge_base_ids=kb_ids,
                created_at=a.created_at
            )
        )
    return result

@router.post("/{advisor_id}/knowledge-bases", response_model=AdvisorRead)
async def link_knowledge_base_to_advisor(
    advisor_id: str,
    payload: LinkKnowledgeBaseRequest,
    db: AsyncSession = Depends(get_db)
):
    """Link a heavy-weight knowledge base to an Advisor."""
    stmt = select(Advisor).where(Advisor.id == advisor_id)
    res = await db.execute(stmt)
    advisor = res.scalar_one_or_none()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")

    link = AdvisorKnowledgeLink(advisor_id=advisor_id, knowledge_base_id=payload.knowledge_base_id)
    db.add(link)
    await db.commit()

    return await list_advisors(db) # re-fetch

# 3. Advisory Consultation & Reviews
@router.post("/consult", response_model=AdvisorySessionRead)
async def request_advisory_consultation(
    payload: AdvisorySessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request consultation or review from the Board of Advisors:
    - Suspends live task lock during intense reasoning.
    - References heavy-weight knowledge bases.
    - Emits multi-step reasoning traces and decisive verdicts.
    - Unfreezes and restores task lock upon completion.
    """
    try:
        session = await AdvisoryEngine.conduct_advisory_review(
            db=db,
            requesting_agent_id=payload.requesting_agent_id,
            advisor_id=payload.advisor_id,
            query_text=payload.query_text,
            correlation_id=payload.correlation_id,
            task_id=payload.task_id,
            request_type=payload.request_type
        )
        await db.commit()
        await db.refresh(session)

        return AdvisorySessionRead(
            id=session.id,
            task_id=session.task_id,
            requesting_agent_id=session.requesting_agent_id,
            advisor_id=session.advisor_id,
            request_type=session.request_type,
            query_text=session.query_text,
            knowledge_references=session.knowledge_references,
            reasoning_trace=session.reasoning_trace,
            verdict=session.verdict,
            advice_summary=session.advice_summary,
            correlation_id=session.correlation_id,
            status=session.status,
            created_at=session.created_at,
            completed_at=session.completed_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advisory session failed: {str(e)}")

@router.get("/sessions", response_model=List[AdvisorySessionRead])
async def list_advisory_sessions(
    task_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List advisory consultation history."""
    stmt = select(AdvisorySession).order_by(AdvisorySession.created_at.desc())
    if task_id:
        stmt = stmt.where(AdvisorySession.task_id == task_id)
    if agent_id:
        stmt = stmt.where(AdvisorySession.requesting_agent_id == agent_id)

    res = await db.execute(stmt)
    sessions = res.scalars().all()

    return [
        AdvisorySessionRead(
            id=s.id,
            task_id=s.task_id,
            requesting_agent_id=s.requesting_agent_id,
            advisor_id=s.advisor_id,
            request_type=s.request_type,
            query_text=s.query_text,
            knowledge_references=s.knowledge_references or [],
            reasoning_trace=s.reasoning_trace,
            verdict=s.verdict,
            advice_summary=s.advice_summary,
            correlation_id=s.correlation_id,
            status=s.status,
            created_at=s.created_at,
            completed_at=s.completed_at
        )
        for s in sessions
    ]
