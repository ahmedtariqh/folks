# Folks: Multi-Agent Orchestration Platform (v1.0)

> **High-Resilience Multi-Agent Orchestrator** integrating a Kanban ticket system with isolated local host execution daemons, dynamic multi-team compilation, rigid state machine governance, and an Owner-exclusive Copilot interface.

---

## Architecture Overview

```
folks/
├── apps/
│   ├── server/                         # FastAPI Orchestrator (State machine, Reaper, Copilot API)
│   │   ├── app/
│   │   │   ├── api/v1/                 # agents, teams, tasks, war_rooms, review_gates, copilot
│   │   │   ├── core/                   # state_machine.py, reaper.py, copilot_engine.py
│   │   │   ├── db/                     # async SQLAlchemy session
│   │   │   ├── schemas/                # Pydantic v2 schemas
│   │   │   └── main.py
│   │   └── tests/                      # Pytest suite (100% pass on state machine & resilience)
│   │
│   └── cockpit/                        # Next.js 15 UI Dashboard (Kanban, War Rooms, Terminal)
│       └── src/
│           ├── app/kanban/page.tsx
│           └── components/
│               ├── copilot-drawer.tsx  # Owner Copilot UI overlay
│               ├── telemetry-terminal.tsx # Real-time daemon stdout/stderr streaming
│               └── review-gate-modal.tsx  # Git diff review & human sign-off
│
├── packages/
│   ├── daemon/                         # Local Host CLI Execution Daemon
│   │   ├── folks_daemon/
│   │   │   ├── client.py               # 15s Heartbeat loop & WebSocket client
│   │   │   ├── executor.py             # Subprocess runner streaming stdout/stderr
│   │   │   └── main.py                 # CLI entry point
│   │   └── tests/
│   │
│   └── db_schema/                      # Centralized SQLAlchemy Models
│       └── models/                     # Agent, Team, Task, WarRoom, ReviewGate, AuditLog
│
└── docker-compose.yml                  # PostgreSQL 16 + Redis 7 + LiteLLM Proxy
```

---

## Core Directives Enforced

### 1. State Machine Resolution: Kanban vs. War Rooms
- **Kanban is Primary, War Rooms are Sub-Routines:** An agent can only enter a War Room if it holds a Kanban task lock (initiator) or is completely `IDLE` (consultant).
- **The Consultant Protocol:** Ephemeral consultants join discussions without checking out duplicate Kanban tickets. When the War Room concludes, consultants return directly to `IDLE`.
- **Lock Suspension:** When an agent pauses for consultation, its task shifts to `PAUSED_FOR_CONSULTATION`. The 60-second lock TTL is frozen to prevent reaper eviction or phantom lock hoarding.
- **Busy Rejection:** Agents actively executing a task auto-reject War Room invites with `AgentBusyError` (`409 Conflict`) to prevent execution drift.
- **Project Tag Security Boundaries:** Task checkout is strictly guarded; agents can only claim tasks matching their assigned `project_tags`.

### 2. The Copilot Boundary: Interface Navigator & BI Analyst
- **Zero Direct SQL / Database Access:** The Owner Copilot has no raw database access or dynamic shell execution capabilities.
- **Rigidly Typed Pydantic APIs:** All mutations are governed by strict schemas (`update_agent_budget`, `assign_project_tag`, `retry_dlq_task`).
- **In-Context UI Map (RAG):** Answers owner queries about settings and controls by providing exact UI breadcrumbs, screen coordinates, and typed action triggers.
- **Diagnostic Trace Interpretation:** Read-only queries of structured `AuditLog` records by `correlation_id`. Translates daemon crashes and timeout reapings into human-readable root causes and concrete remedies.

### 3. Maximum Infrastructure Resilience: Daemon Failure Recovery
- **60-Second Hard Lock TTL:** Tasks in `IN_PROGRESS` hold a temporary database lock expiring in 60s.
- **15-Second Heartbeat Ping:** Local host daemons emit WebSocket pings every 15 seconds to extend the active task's lock TTL.
- **Automatic Reaping to DLQ:** Background sweeper inspects expired locks. If a daemon crashes, OOMs, or loses connection, the task is reaped into the `DEAD_LETTER_QUEUE`, the assigned agent is freed back to `IDLE`, and an alert is emitted.
- **Unified Correlation ID:** Every tool execution, subprocess stdout/stderr emission, and state transition carries a single `correlation_id` tying Agent, Task, and Daemon.

---

## Quickstart Guide

### 1. Run the Orchestrator Server
```bash
# From workspace root:
python -m uvicorn apps.server.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Start the Local Host Execution Daemon
```bash
# Connects to server, handles 15s heartbeats, and executes host CLI tools:
python -m packages.daemon.folks_daemon.main --server ws://127.0.0.1:8000
```

### 3. Run the Automated Test Suite
```bash
# Runs complete state machine, copilot engine, and resilience test suite:
python -m pytest apps/server/tests packages/daemon/tests -v
```
