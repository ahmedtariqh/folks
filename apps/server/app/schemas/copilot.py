from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class UpdateAgentBudgetRequest(BaseModel):
    agent_id: str = Field(..., description="Target Agent UUID")
    monthly_budget_usd: float = Field(..., ge=0.0, le=10000.0, description="New monthly budget cap in USD")

class ToggleFeatureRequest(BaseModel):
    feature_name: str = Field(..., description="Name of the platform feature flag")
    enabled: bool = Field(..., description="Enable or disable flag")

class AssignProjectTagRequest(BaseModel):
    agent_id: str = Field(..., description="Target Agent UUID")
    project_tag: str = Field(..., min_length=2, max_length=100, description="Project tag to grant")

class RetryDLQTaskRequest(BaseModel):
    task_id: str = Field(..., description="Task UUID currently in DEAD_LETTER_QUEUE")
    comment: Optional[str] = Field(None, description="Owner rationale for retry")

class ExplainTraceRequest(BaseModel):
    correlation_id: str = Field(..., description="Correlation ID of the failed execution trace")

class NavigateUIRequest(BaseModel):
    query: str = Field(..., description="Owner query about platform settings, features, or screens")

# Response Schemas
class CopilotActionResponse(BaseModel):
    success: bool
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None

class UINavResult(BaseModel):
    screen_name: str
    route_path: str
    breadcrumbs: List[str]
    description: str
    action_available: Optional[str] = None
    suggested_action_payload: Optional[Dict[str, Any]] = None

class TraceExplanation(BaseModel):
    correlation_id: str
    task_id: Optional[str]
    agent_id: Optional[str]
    daemon_id: Optional[str]
    total_events: int
    has_errors: bool
    root_cause_summary: str
    timeline: List[Dict[str, Any]]
    suggested_remedy: str

