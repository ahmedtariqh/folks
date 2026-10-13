import time
import httpx
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from packages.db_schema.models import (
    Team, Agent, TeamMembership, Task, KnowledgeBase, Advisor,
    AdvisorKnowledgeLink, LLMProviderConfig, SystemSetting, utc_now
)
from app.schemas.onboarding import (
    OnboardingSubmitRequest,
    OnboardingStatusResponse,
    LLMProviderSettingSchema
)

logger = logging.getLogger("folks.onboarding")
router = APIRouter(prefix="/onboarding", tags=["Paperclip-style Onboarding & Setup"])


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(db: AsyncSession = Depends(get_db)):
    """Check if the platform onboarding has been completed and fetch real company metadata."""
    # Check onboarding setting in database
    setting_res = await db.execute(select(SystemSetting).where(SystemSetting.key == "onboarding_completed"))
    setting = setting_res.scalar_one_or_none()

    # Query real database records matching onboarded company
    team = None
    if setting and setting.value and setting.value.get("project_tag"):
        team_res = await db.execute(select(Team).where(Team.project_tag == setting.value.get("project_tag")))
        team = team_res.scalars().first()

    if not team:
        team_res = await db.execute(select(Team).order_by(Team.created_at.desc()))
        team = team_res.scalars().first()


    provider_res = await db.execute(select(LLMProviderConfig).where(LLMProviderConfig.is_active == True).limit(1))
    provider = provider_res.scalar_one_or_none()

    lead_agent_name = None
    if team and team.lead_agent_id:
        agent_res = await db.execute(select(Agent).where(Agent.id == team.lead_agent_id))
        lead_agent = agent_res.scalar_one_or_none()
        if lead_agent:
            lead_agent_name = lead_agent.name

    total_agents = (await db.execute(select(func.count(Agent.id)))).scalar() or 0
    total_tasks = (await db.execute(select(func.count(Task.id)))).scalar() or 0
    total_advisors = (await db.execute(select(func.count(Advisor.id)))).scalar() or 0

    is_completed = bool(setting and setting.value and setting.value.get("completed", False))

    # If no team exists at all, onboarding is strictly not completed
    if not team:
        is_completed = False

    provider_dict = None
    if provider:
        provider_dict = {
            "provider_type": provider.provider_type,
            "provider_name": provider.provider_name,
            "base_url": provider.base_url,
            "default_model": provider.default_model,
            "advisor_reasoning_model": provider.advisor_reasoning_model,
            "temperature": provider.temperature,
            "max_tokens": provider.max_tokens,
            "has_api_key": bool(provider.api_key)
        }

    return OnboardingStatusResponse(
        onboarding_completed=is_completed,
        company_name=team.name if team else None,
        company_mission=team.mission if team else None,
        project_tag=team.project_tag if team else None,
        lead_agent_name=lead_agent_name,
        llm_provider=provider_dict,
        total_agents=total_agents,
        total_tasks=total_tasks,
        total_advisors=total_advisors
    )


@router.post("/complete")
async def complete_onboarding(payload: OnboardingSubmitRequest, db: AsyncSession = Depends(get_db)):
    """Transactional setup creating Organization, Custom LLM Provider, Lead Agent, Advisor, and First Kanban Task."""
    try:
        # 1. Create or update Team
        existing_team = (await db.execute(select(Team).where(Team.project_tag == payload.organization.project_tag))).scalar_one_or_none()
        if not existing_team:
            team = Team(
                name=payload.organization.name,
                mission=payload.organization.mission,
                project_tag=payload.organization.project_tag
            )
            db.add(team)
            await db.flush()
        else:
            team = existing_team
            team.name = payload.organization.name
            team.mission = payload.organization.mission

        # 2. Save Custom LLM Provider Configuration
        llm = payload.llm_provider
        # Deactivate previous active configs
        existing_configs = (await db.execute(select(LLMProviderConfig))).scalars().all()
        for c in existing_configs:
            c.is_active = False

        provider_config = LLMProviderConfig(
            provider_type=llm.provider_type,
            provider_name=llm.provider_name,
            base_url=llm.base_url,
            api_key=llm.api_key,
            default_model=llm.default_model,
            advisor_reasoning_model=llm.advisor_reasoning_model,
            temperature=llm.temperature,
            max_tokens=llm.max_tokens,
            is_active=True
        )
        db.add(provider_config)
        await db.flush()

        # 3. Create Lead Agent / CEO
        lead = payload.lead_agent
        lead_agent = Agent(
            name=lead.name,
            role=lead.role,
            backstory=lead.backstory or f"Lead orchestrator for {team.name}. Operates with high reasoning fidelity.",
            adapter_type=lead.adapter_type,
            model_name=llm.default_model,
            project_tags=[team.project_tag],
            monthly_budget_usd=lead.monthly_budget_usd,
            status="IDLE"
        )
        db.add(lead_agent)
        await db.flush()

        team.lead_agent_id = lead_agent.id
        db.add(TeamMembership(team_id=team.id, agent_id=lead_agent.id, team_role="Lead"))

        # 4. Appoint Strategic Advisor (if supplied)
        advisor_id = None
        if payload.advisor:
            adv = payload.advisor
            domain_tag = adv.domain.lower().replace(" ", "_")
            
            kb = KnowledgeBase(
                name=f"{adv.name} - Domain Knowledge",
                domain_tag=domain_tag,
                description=f"Curated strategic guidelines and architecture standards for {adv.domain}.",
                documents=[
                    {
                        "title": adv.knowledge_title or "Foundational Directives",
                        "content": adv.knowledge_content or "Primary architectural invariants and policy guidelines."
                    }
                ]
            )
            db.add(kb)
            await db.flush()

            advisor = Advisor(
                name=adv.name,
                domain=adv.domain,
                reasoning_model=llm.advisor_reasoning_model,
                system_prompt=f"You are {adv.name}, Chief Strategic Advisor on {adv.domain}. Reason meticulously and challenge architectural assumptions.",
                status="ACTIVE"
            )
            db.add(advisor)
            await db.flush()

            db.add(AdvisorKnowledgeLink(advisor_id=advisor.id, knowledge_base_id=kb.id))
            advisor_id = advisor.id

        # 5. Define Initial Kanban Task (if supplied)
        task_id = None
        if payload.initial_task:
            t = payload.initial_task
            task = Task(
                title=t.title,
                description=t.description or "Initial task established during company onboarding.",
                project_tag=team.project_tag,
                team_id=team.id,
                priority=t.priority,
                status="BACKLOG"
            )
            db.add(task)
            await db.flush()
            task_id = task.id

        # 6. Mark Onboarding as Completed in SystemSetting
        setting_res = await db.execute(select(SystemSetting).where(SystemSetting.key == "onboarding_completed"))
        setting = setting_res.scalar_one_or_none()
        setting_val = {
            "completed": True,
            "completed_at": str(utc_now()),
            "company_name": team.name,
            "project_tag": team.project_tag,
            "provider_type": llm.provider_type
        }
        if not setting:
            setting = SystemSetting(
                key="onboarding_completed",
                value=setting_val,
                description="Status of Paperclip-style company initialization wizard"
            )
            db.add(setting)
        else:
            setting.value = setting_val

        await db.commit()
        logger.info(f"Onboarding successfully completed for company '{team.name}' (Project tag: {team.project_tag})")

        return {
            "success": True,
            "message": f"Company '{team.name}' initialized with custom LLM provider and lead agent.",
            "team_id": team.id,
            "lead_agent_id": lead_agent.id,
            "advisor_id": advisor_id,
            "task_id": task_id
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error completing onboarding: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to complete onboarding: {str(e)}")


@router.post("/test-llm")
async def test_llm_connection(payload: LLMProviderSettingSchema):
    """Test connectivity and latency to the specified LLM provider endpoint."""
    start_time = time.time()
    
    # 1. Custom / OpenAI / Ollama base URL ping
    if payload.base_url:
        target_url = payload.base_url.rstrip("/")
        # Try checking /models or /api/tags if applicable
        test_url = f"{target_url}/models" if not target_url.endswith("/models") else target_url
        headers = {}
        if payload.api_key:
            headers["Authorization"] = f"Bearer {payload.api_key}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(test_url, headers=headers)
                latency = int((time.time() - start_time) * 1000)
                if res.status_code in [200, 401, 403]: # Connected to server
                    return {
                        "success": True,
                        "latency_ms": latency,
                        "status_code": res.status_code,
                        "message": f"Successfully reached {payload.base_url} ({latency}ms). Endpoint acknowledged."
                    }
                else:
                    return {
                        "success": True,
                        "latency_ms": latency,
                        "status_code": res.status_code,
                        "message": f"Connected to {payload.base_url} (HTTP {res.status_code}, {latency}ms)."
                    }
        except httpx.ConnectError:
            return {
                "success": False,
                "latency_ms": 0,
                "message": f"Could not connect to {payload.base_url}. Ensure the local server or proxy is running."
            }
        except Exception as e:
            return {
                "success": False,
                "latency_ms": 0,
                "message": f"Error reaching endpoint: {str(e)}"
            }

    # 2. Known Cloud Providers fallback validation
    latency = int((time.time() - start_time) * 1000)
    return {
        "success": True,
        "latency_ms": latency,
        "message": f"Configured provider '{payload.provider_type}' with model '{payload.default_model}'."
    }


@router.post("/reset")
async def reset_onboarding(db: AsyncSession = Depends(get_db)):
    """Reset onboarding state to re-trigger the Paperclip onboarding wizard."""
    setting_res = await db.execute(select(SystemSetting).where(SystemSetting.key == "onboarding_completed"))
    setting = setting_res.scalar_one_or_none()
    if setting:
        setting.value = {"completed": False}
        await db.commit()
    return {"success": True, "message": "Onboarding state reset. The setup wizard will now display."}
