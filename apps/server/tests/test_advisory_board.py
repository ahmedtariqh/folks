import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from packages.db_schema.models import Agent, Task, KnowledgeBase, Advisor, AdvisorKnowledgeLink
from app.core.advisory_engine import AdvisoryEngine
from app.core.state_machine import OrchestratorStateMachine
from app.core.copilot_engine import OwnerCopilotEngine

@pytest.mark.asyncio
async def test_create_and_query_board_of_advisors(db_session):
    # 1. Create a Heavy-Weight Knowledge Base
    kb = KnowledgeBase(
        name="Enterprise Cloud & Microservices Standards",
        domain_tag="distributed_systems",
        description="Comprehensive architectural guidelines, idempotency guarantees, and retry budgets.",
        documents=[
            {
                "title": "Distributed Concurrency & Locks Standard",
                "content": "All execution locks must implement monotonic TTL countdowns and lease renewals via heartbeat pings. Zombie locks must be reaped to DLQ after 60 seconds."
            },
            {
                "title": "Idempotent Webhook Processing",
                "content": "Payment webhooks must verify payload signatures and store idempotency keys in Redis before mutating database states."
            }
        ]
    )
    db_session.add(kb)
    await db_session.flush()

    # 2. Appoint an Advisor with intense reasoning model
    advisor = Advisor(
        name="Dr. Marcus Vance",
        domain="DISTRIBUTED_SYSTEMS",
        reasoning_model="claude-3-7-sonnet-thought",
        system_prompt="You are a Principal Enterprise Systems Architect. Analyze trade-offs rigorously against cited standards.",
        status="ACTIVE"
    )
    db_session.add(advisor)
    await db_session.flush()

    # Link Knowledge Base to Advisor
    link = AdvisorKnowledgeLink(advisor_id=advisor.id, knowledge_base_id=kb.id)
    db_session.add(link)
    await db_session.commit()

    # 3. Create an agent and task
    agent = Agent(name="Lead Dev", role="Architect", project_tags=["proj_payments"])
    task = Task(title="Design Webhook Handler", project_tag="proj_payments", status="QUEUED")
    db_session.add_all([agent, task])
    await db_session.commit()

    # Checkout task (agent now holds active lock)
    await OrchestratorStateMachine.checkout_task(
        db=db_session,
        agent_id=agent.id,
        task_id=task.id,
        correlation_id="corr-advisor-test-1",
        lock_ttl_seconds=60
    )
    assert task.status == "IN_PROGRESS"
    assert task.lock_suspended is False

    # 4. Agent reaches out to Advisor for architectural review
    session = await AdvisoryEngine.conduct_advisory_review(
        db=db_session,
        requesting_agent_id=agent.id,
        advisor_id=advisor.id,
        query_text="How should we implement Stripe webhook locks and idempotency keys to ensure resilience?",
        correlation_id="corr-advisor-test-1",
        task_id=task.id,
        request_type="ARCHITECTURE_ADVICE"
    )

    # 5. Verify intense reasoning and knowledge base citations
    assert session.status == "COMPLETED"
    assert len(session.knowledge_references) > 0
    assert any("Distributed Concurrency" in ref["title"] or "Idempotent Webhook" in ref["title"] for ref in session.knowledge_references)
    assert session.reasoning_trace is not None
    assert "Step 1 [Context Evaluation]" in session.reasoning_trace
    assert "Step 4 [Synthesis & Trade-offs]" in session.reasoning_trace
    assert session.verdict in ("RECOMMENDATIONS_PROVIDED", "APPROVED")

    # 6. Verify task lock was preserved and resumed back to IN_PROGRESS
    assert task.status == "IN_PROGRESS"
    assert task.lock_suspended is False
    assert task.lock_expires_at is not None


@pytest.mark.asyncio
async def test_advisory_verdict_risk_detection(db_session):
    advisor = Advisor(
        name="Sophia Thorne",
        domain="CYBERSECURITY",
        reasoning_model="o3-mini-high",
        system_prompt="Security auditor reviewing code and architectural proposals.",
        status="ACTIVE"
    )
    agent = Agent(name="Junior Dev", role="Engineer", project_tags=["proj_auth"])
    db_session.add_all([advisor, agent])
    await db_session.commit()

    session = await AdvisoryEngine.conduct_advisory_review(
        db=db_session,
        requesting_agent_id=agent.id,
        advisor_id=advisor.id,
        query_text="We have a security flaw and vulnerability in the auth token signing routine.",
        correlation_id="corr-sec-alert",
        request_type="SECURITY_REVIEW"
    )

    assert session.verdict == "RISK_FLAGGED"
    assert "flagged critical risks" in session.advice_summary


def test_copilot_navigation_to_board_of_advisors():
    results = OwnerCopilotEngine.navigate_ui("How do I contact the board of advisors for architecture reviews?")
    assert len(results) > 0
    top = results[0]
    assert top.route_path == "/advisors"
    assert "Board of Advisors" in top.screen_name
    assert top.action_available == "request_advisory_consultation"
