from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Knowledge Base Schemas
class KnowledgeBaseDocument(BaseModel):
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str = ""
    domain_tag: str = Field(..., max_length=100)
    documents: List[KnowledgeBaseDocument] = Field(default_factory=list)

class KnowledgeBaseRead(BaseModel):
    id: str
    name: str
    description: str
    domain_tag: str
    documents: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Advisor Schemas
class AdvisorCreate(BaseModel):
    name: str = Field(..., max_length=255)
    domain: str = Field(..., max_length=100)
    reasoning_model: str = "claude-3-7-sonnet-thought"
    system_prompt: str
    knowledge_base_ids: List[str] = Field(default_factory=list)

class AdvisorRead(BaseModel):
    id: str
    name: str
    domain: str
    reasoning_model: str
    system_prompt: str
    status: str
    linked_knowledge_base_ids: List[str] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LinkKnowledgeBaseRequest(BaseModel):
    knowledge_base_id: str

# Advisory Session Schemas
class AdvisorySessionRequest(BaseModel):
    requesting_agent_id: str
    advisor_id: str
    task_id: Optional[str] = None
    request_type: str = "ARCHITECTURE_ADVICE" # ARCHITECTURE_ADVICE, SECURITY_REVIEW, STRATEGIC_DIRECTION, PRE_GATE_AUDIT
    query_text: str
    correlation_id: str

class AdvisorySessionRead(BaseModel):
    id: str
    task_id: Optional[str]
    requesting_agent_id: str
    advisor_id: str
    advisor_name: Optional[str] = None
    request_type: str
    query_text: str
    knowledge_references: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_trace: Optional[str] = None
    verdict: str
    advice_summary: Optional[str] = None
    correlation_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
