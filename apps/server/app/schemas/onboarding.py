from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LLMProviderSettingSchema(BaseModel):
    provider_type: str = Field(default="custom", description="custom, ollama, anthropic, openai, openrouter, gemini")
    provider_name: str = Field(default="Custom LLM Gateway")
    base_url: Optional[str] = Field(default=None, description="Base URL e.g. http://localhost:11434/v1 or custom OpenAI-compatible endpoint")
    api_key: Optional[str] = Field(default=None, description="API Key or Bearer Token (optional for local models)")
    default_model: str = Field(default="claude-3-7-sonnet", description="Model identifier for standard agents")
    advisor_reasoning_model: str = Field(default="claude-3-7-sonnet-thought", description="Deep reasoning model for Board of Advisors")
    temperature: Optional[float] = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=4096)

class OnboardingOrganizationSchema(BaseModel):
    name: str = Field(default="Apex Autonomous Labs", description="Company or Team name")
    mission: Optional[str] = Field(default="", description="High-level company mission and operating directives")
    project_tag: str = Field(default="folks_core", description="Project tag")

class OnboardingLeadAgentSchema(BaseModel):
    name: str = Field(default="Nova - Lead Orchestrator", description="Agent name")
    role: str = Field(default="Lead Orchestrator")
    backstory: Optional[str] = Field(default="")
    adapter_type: str = Field(default="host_cli")
    monthly_budget_usd: Optional[float] = Field(default=100.0)

class OnboardingAdvisorSchema(BaseModel):
    name: Optional[str] = Field(default="Dr. Aris Thorne")
    domain: Optional[str] = Field(default="Distributed Systems & Resilience")
    knowledge_title: Optional[str] = Field(default="Lock Invariants and Sweeper Policies")
    knowledge_content: Optional[str] = Field(default="State machine invariants: Kanban holds primary lock, War Rooms are ephemeral subroutines. Heartbeats must ping every 15s; expired locks must reap to DLQ.")

class OnboardingTaskSchema(BaseModel):
    title: Optional[str] = Field(default="Confirm system readiness, tool availability, and knowledge base access")
    description: Optional[str] = Field(default="Verify that the execution daemon, LLM provider, available tools, and domain knowledge bases are fully accessible and operating correctly.")
    priority: Optional[str] = Field(default="HIGH")


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

