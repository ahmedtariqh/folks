from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.copilot import (
    NavigateUIRequest,
    UINavResult,
    ExplainTraceRequest,
    TraceExplanation,
    UpdateAgentBudgetRequest,
    AssignProjectTagRequest,
    RetryDLQTaskRequest,
    CopilotActionResponse
)
from app.core.copilot_engine import OwnerCopilotEngine

router = APIRouter(prefix="/owner/copilot", tags=["Owner Copilot"])

@router.post("/navigate", response_model=List[UINavResult])
async def navigate_ui(req: NavigateUIRequest):
    return OwnerCopilotEngine.navigate_ui(req.query)

@router.post("/explain-trace", response_model=TraceExplanation)
async def explain_trace(req: ExplainTraceRequest, db: AsyncSession = Depends(get_db)):
    return await OwnerCopilotEngine.explain_trace(db, req.correlation_id)

@router.post("/action/budget", response_model=CopilotActionResponse)
async def update_agent_budget(req: UpdateAgentBudgetRequest, db: AsyncSession = Depends(get_db)):
    res = await OwnerCopilotEngine.update_agent_budget(db, req)
    if not res.success:
        raise HTTPException(status_code=400, detail=res.message)
    return res

@router.post("/action/assign-tag", response_model=CopilotActionResponse)
async def assign_project_tag(req: AssignProjectTagRequest, db: AsyncSession = Depends(get_db)):
    res = await OwnerCopilotEngine.assign_project_tag(db, req)
    if not res.success:
        raise HTTPException(status_code=400, detail=res.message)
    return res

@router.post("/action/retry-dlq", response_model=CopilotActionResponse)
async def retry_dlq_task(req: RetryDLQTaskRequest, db: AsyncSession = Depends(get_db)):
    res = await OwnerCopilotEngine.retry_dlq_task(db, req)
    if not res.success:
        raise HTTPException(status_code=400, detail=res.message)
    return res
