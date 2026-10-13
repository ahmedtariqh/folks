import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import init_db

@pytest.mark.asyncio
async def test_full_platform_api_workflow():
    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check & Server Dashboard
        res_health = await client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"

        res_dash = await client.get("/")
        assert res_dash.status_code == 200
        assert "FOLKS" in res_dash.text
        assert "Kanban Board" in res_dash.text

        res_dash2 = await client.get("/dashboard")
        assert res_dash2.status_code == 200

        # Verify system overview endpoint
        res_overview = await client.get("/api/v1/system/overview")
        assert res_overview.status_code == 200
        assert res_overview.json()["status"] == "HEALTHY"
        assert res_overview.json()["sweeper"]["status"] == "ACTIVE"

        # Verify system demo seed endpoint
        res_seed = await client.post("/api/v1/system/seed")
        assert res_seed.status_code == 200
        assert res_seed.json()["status"] == "success"

        # 2. Create Agents in Pool
        res_ag1 = await client.post("/api/v1/agents", json={
            "name": "Alice Architect",
            "role": "System Architect",
            "project_tags": ["proj_payments", "proj_core"],
            "monthly_budget_usd": 100.0
        })
        assert res_ag1.status_code == 200
        agent_1 = res_ag1.json()

        res_ag2 = await client.post("/api/v1/agents", json={
            "name": "Bob Coder",
            "role": "Backend Engineer",
            "project_tags": ["proj_payments"],
            "monthly_budget_usd": 50.0
        })
        assert res_ag2.status_code == 200
        agent_2 = res_ag2.json()

        # 3. Dynamically Compile a Virtual Team
        res_team = await client.post("/api/v1/teams/compile", json={
            "name": "Payments Squad Alpha",
            "project_tag": "proj_payments",
            "lead_agent_id": agent_1["id"],
            "member_assignments": [
                {"agent_id": agent_2["id"], "team_role": "Specialist"}
            ]
        })
        assert res_team.status_code == 200
        team = res_team.json()
        assert len(team["members"]) == 2

        # 4. Create a Kanban Task
        res_task = await client.post("/api/v1/tasks", json={
            "title": "Migrate Payment Webhooks to Stripe v2024",
            "project_tag": "proj_payments",
            "team_id": team["id"],
            "priority": "HIGH"
        })
        assert res_task.status_code == 200
        task = res_task.json()
        assert task["status"] == "BACKLOG"

        # 5. Atomic Checkout by Bob (matching project tag)
        res_checkout = await client.post(f"/api/v1/tasks/{task['id']}/checkout", json={
            "agent_id": agent_2["id"],
            "daemon_id": "daemon-host-win-01",
            "correlation_id": "corr-integ-test-44",
            "lock_ttl_seconds": 60
        })
        assert res_checkout.status_code == 200
        checked_task = res_checkout.json()
        assert checked_task["status"] == "IN_PROGRESS"
        assert checked_task["lock_owner_id"] == "daemon-host-win-01"

        # 6. Owner Copilot Navigation Query (RAG over platform UI catalog)
        res_nav = await client.post("/api/v1/owner/copilot/navigate", json={
            "query": "Where do I adjust the monthly spend cap for Bob?"
        })
        assert res_nav.status_code == 200
        nav_results = res_nav.json()
        assert any(n["route_path"] == "/settings/agents" for n in nav_results)

        # 7. Owner Copilot updates Bob's budget via strictly typed API (Zero SQL)
        res_budget = await client.post("/api/v1/owner/copilot/action/budget", json={
            "agent_id": agent_2["id"],
            "monthly_budget_usd": 120.0
        })
        assert res_budget.status_code == 200
        assert res_budget.json()["success"] is True

        # 8. Submit Diff to Review Gate
        res_gate = await client.post("/api/v1/review-gates", json={
            "task_id": task["id"],
            "agent_id": agent_2["id"],
            "diff_patch": "--- a/src/webhook.py\n+++ b/src/webhook.py\n@@ -1,3 +1,4 @@\n+import stripe\n",
            "correlation_id": "corr-integ-test-44"
        })
        assert res_gate.status_code == 200
        gate = res_gate.json()
        assert gate["status"] == "PENDING"

        # 9. Verify task status moved to AWAITING_REVIEW
        res_task_updated = await client.get(f"/api/v1/tasks/{task['id']}")
        assert res_task_updated.json()["status"] == "AWAITING_REVIEW"

        # 10. Human Owner Approves Review Gate
        res_approve = await client.post(f"/api/v1/review-gates/{gate['id']}/action", json={
            "action": "APPROVE",
            "feedback": "LGTM, clean migration!"
        })
        assert res_approve.status_code == 200
        assert res_approve.json()["status"] == "APPROVED"

        # 11. Final verification: Task is DONE and Agent Bob is back to IDLE
        res_task_final = await client.get(f"/api/v1/tasks/{task['id']}")
        assert res_task_final.json()["status"] == "DONE"

        res_agent_final = await client.get(f"/api/v1/agents/{agent_2['id']}")
        assert res_agent_final.json()["status"] == "IDLE"
