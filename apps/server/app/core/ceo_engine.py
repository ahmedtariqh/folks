import re
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from packages.db_schema.models import (
    Team, Agent, TeamMembership, Task, Advisor, AuditLog, AgentMessage, LLMProviderConfig, utc_now
)

logger = logging.getLogger("folks.ceo_engine")

class CEOEngine:
    """Executive brain of the CEO / Lead Orchestrator agent.
    Has full authority to delegate tasks, inspect reports, and orchestrate across teams.
    """

    @staticmethod
    async def process_ceo_directive(
        db: AsyncSession,
        user_message: str,
        project_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Fetch Primary Organization & CEO Agent
        team_stmt = select(Team)
        if project_tag:
            team_stmt = team_stmt.where(Team.project_tag == project_tag)
        else:
            team_stmt = team_stmt.order_by(Team.created_at.desc())
        
        team_res = await db.execute(team_stmt)
        team = team_res.scalars().first()

        if not team:
            # Fallback if no team exists yet
            return {
                "response": "No active organization found in database. Please complete the setup wizard first.",
                "intent": "ERROR",
                "actions_taken": []
            }

        ceo_agent = None
        if team.lead_agent_id:
            ceo_res = await db.execute(select(Agent).where(Agent.id == team.lead_agent_id))
            ceo_agent = ceo_res.scalar_one_or_none()

        if not ceo_agent:
            # Pick any agent if lead is unset
            any_agent_res = await db.execute(select(Agent).limit(1))
            ceo_agent = any_agent_res.scalar_one_or_none()

        ceo_name = ceo_agent.name if ceo_agent else "Chief Executive Agent"
        ceo_id = ceo_agent.id if ceo_agent else "ceo-lead"

        # 2. Gather Real Platform Operational State
        tasks_res = await db.execute(select(Task).where(Task.project_tag == team.project_tag))
        all_tasks = tasks_res.scalars().all()

        tasks_by_status = {}
        for t in all_tasks:
            tasks_by_status[t.status] = tasks_by_status.get(t.status, 0) + 1

        agents_res = await db.execute(select(Agent))
        all_agents = agents_res.scalars().all()
        agent_names_map = {a.name.lower(): a for a in all_agents}

        msg_lower = user_message.lower().strip()
        actions_taken = []
        intent = "GENERAL_STRATEGY"
        report_data = None

        # 3. Intent Detection: Status Report
        is_report_request = any(k in msg_lower for k in [
            "report", "status", "progress", "update", "how are we doing", "overview", "what are we working on", "health"
        ])

        # Intent Detection: Task Delegation / Work Assignment
        is_delegation_request = any(k in msg_lower for k in [
            "delegate", "assign", "create task", "add task", "new task", "make a task", "tell ", "have ", "instruct "
        ]) or msg_lower.startswith("task:")

        if is_report_request and not is_delegation_request:
            intent = "STATUS_REPORT"
            in_prog = tasks_by_status.get("IN_PROGRESS", 0)
            paused = tasks_by_status.get("PAUSED_FOR_CONSULTATION", 0)
            dlq = tasks_by_status.get("DEAD_LETTER_QUEUE", 0)
            backlog = tasks_by_status.get("BACKLOG", 0) + tasks_by_status.get("TODO", 0) + tasks_by_status.get("QUEUED", 0)
            completed = tasks_by_status.get("DONE", 0) + tasks_by_status.get("COMPLETED", 0)

            report_data = {
                "organization": team.name,
                "project_tag": team.project_tag,
                "total_tasks": len(all_tasks),
                "in_progress": in_prog,
                "paused_consultation": paused,
                "dlq_reaped": dlq,
                "backlog_queue": backlog,
                "completed": completed,
                "active_agents": len(all_agents),
                "tasks_count": {
                    "total": len(all_tasks),
                    "in_progress": in_prog,
                    "paused_for_consultation": paused,
                    "dlq": dlq,
                    "backlog": backlog,
                    "completed": completed
                }
            }

            response_text = (
                f"**Executive Status Report for {team.name}**\n\n"
                f"• **Active Tasks in Progress:** {in_prog} (holding active lock leases)\n"
                f"• **Backlog / Queue:** {backlog} tasks awaiting checkout\n"
                f"• **Paused for Consultation:** {paused} tasks (TTL frozen under Consultant Protocol)\n"
                f"• **Dead-Letter Queue (DLQ):** {dlq} reaped tasks requiring review\n"
                f"• **Completed Deliverables:** {completed}\n"
                f"• **Total Available Agents:** {len(all_agents)}\n\n"
            )

            if dlq > 0:
                response_text += f"⚠️ **Attention Required:** There are {dlq} tasks in the Dead-Letter Queue due to expired locks or missing heartbeats.\n"
            else:
                response_text += f"✅ **Operational Status:** All system state machines are healthy. 15s heartbeats and sweeper loops are aligned.\n"

            response_text += "Instruct me anytime if you want to delegate a new task, reprioritize tickets, or adjust agent assignments."

        elif is_delegation_request:
            intent = "TASK_DELEGATION"

            # Parse target agent if mentioned
            target_agent = None
            for name_k, ag in agent_names_map.items():
                first_name = name_k.split()[0]
                if first_name in msg_lower or name_k in msg_lower:
                    target_agent = ag
                    break

            # Parse priority
            priority = "MEDIUM"
            if "urgent" in msg_lower or "critical" in msg_lower:
                priority = "URGENT"
            elif "high" in msg_lower:
                priority = "HIGH"
            elif "low" in msg_lower:
                priority = "LOW"

            # Extract clean task title from directive
            quoted_match = re.search(r'["\']([^"\']+)["\']', user_message)
            if quoted_match:
                clean_title = quoted_match.group(1).strip()
            else:
                clean_title = user_message
                for prefix in [
                    "delegate task:", "delegate task", "delegate:", "delegate",
                    "assign a task to", "create a task to", "create task to",
                    "create task:", "create task", "add task:", "add task", "task:"
                ]:
                    if clean_title.lower().startswith(prefix):
                        clean_title = clean_title[len(prefix):].strip()
                        break
                clean_title = clean_title.strip().strip('"').strip("'")

            if len(clean_title) > 100:
                clean_title = clean_title[:97] + "..."

            # Create Task in Database
            new_task = Task(
                title=clean_title,
                description=f"Executive directive delegated by {ceo_name}: {user_message}",
                project_tag=team.project_tag,
                team_id=team.id,
                assigned_agent_id=target_agent.id if target_agent else None,
                priority=priority,
                status="BACKLOG"
            )
            db.add(new_task)
            await db.flush()

            # Record CEO Audit Event
            audit = AuditLog(
                correlation_id=f"ceo-del-{new_task.id[:8]}",
                agent_id=ceo_id,
                task_id=new_task.id,
                event_type="CEO_DELEGATION",
                level="INFO",
                message=f"CEO delegated Task '{new_task.title}' [Priority: {priority}] to {target_agent.name if target_agent else 'General Backlog'}.",
                payload={"target_agent_id": target_agent.id if target_agent else None, "priority": priority}
            )
            db.add(audit)
            await db.commit()

            actions_taken.append({
                "action": "TASK_CREATED",
                "task_id": new_task.id,
                "title": new_task.title,
                "assigned_to": target_agent.name if target_agent else "Backlog Pool",
                "assigned_agent_name": target_agent.name if target_agent else "Backlog Pool",
                "priority": priority
            })

            target_msg = f"assigned to **{target_agent.name}**" if target_agent else "placed into the **Backlog Queue** for checkout"
            response_text = (
                f"Understood. As CEO, I have established and registered the task:\n\n"
                f"📋 **Ticket:** *{new_task.title}*\n"
                f"⚡ **Priority:** {priority}\n"
                f"👤 **Assignment:** {target_msg}\n"
                f"🏷️ **Project Scope:** `{team.project_tag}`\n\n"
                f"The task is now live in the Kanban system. The companion execution daemons will proceed according to state machine priority."
            )

        else:
            # Strategic Consultation
            intent = "STRATEGIC_ADVICE"
            response_text = (
                f"Greetings. I am **{ceo_name}**, leading operations for **{team.name}**.\n\n"
                f"Our primary mission: *\"{team.mission or 'Autonomous Engineering Execution'}\"*.\n\n"
                f"I oversee all virtual squads and enforce state machine invariants across our Kanban board. "
                f"You can instruct me to:\n"
                f"1. **Delegate Work:** e.g. *\"Assign a task to Forge to verify socket telemetry\"* or *\"Create urgent task to patch auth\"*\n"
                f"2. **Request Reports:** e.g. *\"Give me a status report on active tasks and blockers\"*\n"
                f"3. **Adjust Squads:** reassign tasks or coordinate sub-routines.\n\n"
                f"How would you like to direct our organization today?"
            )

        # 4. Save dialogue to AgentMessage history if ceo_agent exists
        if ceo_agent:
            db.add(AgentMessage(
                agent_id=ceo_agent.id,
                sender_type="USER",
                message=user_message,
                message_type="CHAT"
            ))
            db.add(AgentMessage(
                agent_id=ceo_agent.id,
                sender_type="AGENT",
                message=response_text,
                message_type=intent,
                metadata_payload={"actions": actions_taken, "report": report_data}
            ))
            await db.commit()

        return {
            "response": response_text,
            "intent": intent,
            "ceo_name": ceo_name,
            "ceo_role": ceo_agent.role if ceo_agent else "CEO",
            "actions_taken": actions_taken,
            "report_data": report_data
        }
