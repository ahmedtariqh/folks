import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import init_db

@pytest.mark.asyncio
async def test_onboarding_lifecycle_and_custom_llm():
    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Reset onboarding to ensure clean state
        res_reset = await client.post("/api/v1/onboarding/reset")
        assert res_reset.status_code == 200

        # 2. Check initial onboarding status (should indicate not completed)
        res_status = await client.get("/api/v1/onboarding/status")
        assert res_status.status_code == 200
        status_data = res_status.json()
        assert status_data["onboarding_completed"] is False

        # 3. Test LLM provider connection endpoint
        res_test_llm = await client.post("/api/v1/onboarding/test-llm", json={
            "provider_type": "custom",
            "provider_name": "Local Ollama Gateway",
            "base_url": "http://localhost:11434/v1",
            "default_model": "llama3.3:70b",
            "advisor_reasoning_model": "deepseek-r1"
        })
        assert res_test_llm.status_code == 200
        llm_test_res = res_test_llm.json()
        assert "message" in llm_test_res

        # 4. Complete Onboarding with Custom LLM Provider and Company setup
        res_complete = await client.post("/api/v1/onboarding/complete", json={
            "organization": {
                "name": "Starlight Autonomous Corp",
                "mission": "Orchestrate high-reliability autonomous development squads with strict state machines.",
                "project_tag": "starlight_core"
            },
            "llm_provider": {
                "provider_type": "custom",
                "provider_name": "Custom OpenAI-compatible Proxy",
                "base_url": "https://api.openai.com/v1",
                "api_key": "sk-test-key-12345",
                "default_model": "gpt-4o",
                "advisor_reasoning_model": "o3-mini",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            "lead_agent": {
                "name": "Orion - Lead Architect",
                "role": "Chief Orchestrator",
                "backstory": "Directs asynchronous execution threads and coordinates Kanban task checkouts.",
                "adapter_type": "host_cli",
                "monthly_budget_usd": 150.0
            },
            "advisor": {
                "name": "Dr. Vanessa Cruz",
                "domain": "DISTRIBUTED_SYSTEMS",
                "knowledge_title": "Fencing Tokens and Lock Sweeper Invariants",
                "knowledge_content": "Expired locks must be deterministically swept to DLQ. 15s heartbeats must be enforced."
            },
            "initial_task": {
                "title": "Establish Host Daemon Socket Handshake",
                "description": "Connect execution daemon to /ws/daemon/{daemon_id} and stream stdout.",
                "priority": "HIGH"
            }
        })
        assert res_complete.status_code == 200
        complete_data = res_complete.json()
        assert complete_data["success"] is True
        assert complete_data["team_id"] is not None
        assert complete_data["lead_agent_id"] is not None

        # 5. Check onboarding status again (now completed)
        res_status_after = await client.get("/api/v1/onboarding/status")
        assert res_status_after.status_code == 200
        after_data = res_status_after.json()
        assert after_data["onboarding_completed"] is True
        assert after_data["company_name"] == "Starlight Autonomous Corp"
        assert after_data["lead_agent_name"] == "Orion - Lead Architect"
        assert after_data["llm_provider"]["provider_type"] == "custom"
        assert after_data["llm_provider"]["default_model"] == "gpt-4o"
        assert after_data["total_agents"] >= 1
        assert after_data["total_tasks"] >= 1
