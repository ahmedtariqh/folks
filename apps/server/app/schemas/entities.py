from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# 1. Agent Schemas
class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    role: str = Field(..., max_length=100)
    backstory: str = ""
    adapter_type: str = "host_cli"
    model_name: str = "claude-3-7-sonnet"
    project_tags: List[str] = Field(default_factory=list)
    monthly_budget_usd: float = 50.0

class AgentCreate(AgentBase):
    pass

class AgentRead(AgentBase):
    id: str
    current_spend_usd: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 2. Team Schemas
class TeamCreate(BaseModel):
    name: str = Field(..., max_length=255)
    project_tag: str = Field(..., max_length=100)
    lead_agent_id: Optional[str] = None
    member_agent_ids: List[str] = Field(default_factory=list)

class TeamMemberInfo(BaseModel):
    agent_id: str
    agent_name: str
    role: str
    team_role: str

class TeamRead(BaseModel):
    id: str
    name: str
    project_tag: str
    lead_agent_id: Optional[str]
    members: List[TeamMemberInfo] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CompileTeamRequest(BaseModel):
    name: str
    project_tag: str
    lead_agent_id: str
    member_assignments: List[Dict[str, str]]

# 3. Task Schemas
class TaskCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str = ""
    project_tag: str = Field(..., max_length=100)
    priority: str = "MEDIUM"
    team_id: Optional[str] = None

class TaskCheckoutRequest(BaseModel):
    agent_id: str
    daemon_id: Optional[str] = None
    correlation_id: str
    lock_ttl_seconds: int = 60

class TaskSuspendRequest(BaseModel):
    correlation_id: str

class TaskResumeRequest(BaseModel):
    correlation_id: str

class TaskRead(BaseModel):
    id: str
    title: str
    description: str
    project_tag: str
    status: str
    priority: str
    assigned_agent_id: Optional[str] = None
    team_id: Optional[str] = None
    lock_owner_id: Optional[str] = None
    lock_expires_at: Optional[datetime] = None
    lock_ttl_seconds: int
    lock_suspended: bool
    lock_suspended_remaining_seconds: Optional[int] = None
    correlation_id: Optional[str] = None
    blocker_reason: Optional[str] = None
    dlq_reason: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 4. War Room Schemas
class WarRoomCreate(BaseModel):
    task_id: str
    initiator_agent_id: str
    title: str
    invitee_agent_ids: List[str] = Field(default_factory=list)
    correlation_id: str

class WarRoomMessageCreate(BaseModel):
    sender_type: str = "AGENT"
    agent_id: Optional[str] = None
    content: str
    correlation_id: Optional[str] = None

class WarRoomMessageRead(BaseModel):
    id: str
    war_room_id: str
    sender_type: str
    agent_id: Optional[str]
    content: str
    correlation_id: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WarRoomRead(BaseModel):
    id: str
    task_id: str
    title: str
    initiator_agent_id: str
    status: str
    created_at: datetime
    concluded_at: Optional[datetime]
    accepted_agents: List[str] = Field(default_factory=list)
    rejected_agents: List[str] = Field(default_factory=list)

# 5. Review Gate Schemas
class ReviewGateCreate(BaseModel):
    task_id: str
    agent_id: str
    diff_patch: str
    test_results: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None

class ReviewGateActionRequest(BaseModel):
    action: str = Field(..., pattern="^(APPROVE|REJECT)$")
    feedback: Optional[str] = None

class ReviewGateRead(BaseModel):
    id: str
    task_id: str
    agent_id: str
    diff_patch: str
    test_results: Optional[Dict[str, Any]]
    status: str
    owner_feedback: Optional[str]
    correlation_id: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
