from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LLMProviderSettingSchema(BaseModel):
    provider_type: str = Field(default="custom", description="custom, ollama, anthropic, openai, openrouter, gemini")
    provider_name: str = Field(default="Custom LLM Gateway")
    base_url: Optional[str] = Field(default=None, description="Base URL e.g. http://localhost:11434/v1 or custom OpenAI-compatible endpoint")
    api_key: Optional[str] = Field(default=None, description="API Key or Bearer Token (optional for local models)")
    default_model: str = Field(default="claude-3-7-sonnet", description="Model identifier for standard agents")
    advisor_reasoning_model: str = Field(default="claude-3-7-sonnet-thought", description="Deep reasoning model for Board of Advisors")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=256, le=128000)

class OnboardingOrganizationSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Company or Team name")
    mission: str = Field(..., min_length=5, description="High-level company mission and operating directives")
    project_tag: str = Field(default="folks_core", min_length=2, max_length=100)

class OnboardingLeadAgentSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default="Lead Orchestrator")
    backstory: Optional[str] = Field(default="")
    adapter_type: str = Field(default="host_cli")
    monthly_budget_usd: float = Field(default=100.0, ge=0.0)

class OnboardingAdvisorSchema(BaseModel):
    name: str = Field(default="Dr. Aris Thorne")
    domain: str = Field(default="DISTRIBUTED_SYSTEMS")
    knowledge_title: Optional[str] = Field(default="Distributed Consensus & Lock Invariants")
    knowledge_content: Optional[str] = Field(default="State machine invariants: Kanban holds primary lock, War Rooms are ephemeral subroutines. Heartbeats must ping every 15s; expired locks must reap to DLQ.")

class OnboardingTaskSchema(BaseModel):
    title: str = Field(default="Verify Local Host Daemon 15s Heartbeat Ping")
    description: Optional[str] = Field(default="Establish WebSocket handshake with /ws/daemon/{daemon_id} and maintain 15-second heartbeat intervals.")
    priority: str = Field(default="HIGH")

class OnboardingSubmitRequest(BaseModel):
    organization: OnboardingOrganizationSchema
    llm_provider: LLMProviderSettingSchema
    lead_agent: OnboardingLeadAgentSchema
    advisor: Optional[OnboardingAdvisorSchema] = None
    initial_task: Optional[OnboardingTaskSchema] = None

class OnboardingStatusResponse(BaseModel):
    onboarding_completed: bool
    company_name: Optional[str] = None
    company_mission: Optional[str] = None
    project_tag: Optional[str] = None
    lead_agent_name: Optional[str] = None
    llm_provider: Optional[Dict[str, Any]] = None
    total_agents: int = 0
    total_tasks: int = 0
    total_advisors: int = 0
