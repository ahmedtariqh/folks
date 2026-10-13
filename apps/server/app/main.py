import sys
from pathlib import Path

# Ensure apps/server and project root are always in sys.path
SERVER_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SERVER_ROOT.parent.parent
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.db.session import init_db
from app.core.reaper import run_lock_sweeper_loop

from app.api.v1.agents import router as agents_router
from app.api.v1.teams import router as teams_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.war_rooms import router as war_rooms_router
from app.api.v1.copilot import router as copilot_router
from app.api.v1.review_gates import router as review_gates_router
from app.api.v1.advisors import router as advisors_router
from app.api.v1.system import router as system_router
from app.api.v1.onboarding import router as onboarding_router
from app.api.websockets import router as ws_router
from app.templates.dashboard import get_dashboard_html


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("folks.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Folks Orchestrator database schema...")
    await init_db()

    logger.info("Spawning background lock sweeper task (Resilience & DLQ Reaper)...")
    sweeper_task = asyncio.create_task(run_lock_sweeper_loop())

    yield

    logger.info("Shutting down Folks Orchestrator...")
    sweeper_task.cancel()
    try:
        await sweeper_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(teams_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)
app.include_router(war_rooms_router, prefix=settings.API_V1_STR)
app.include_router(copilot_router, prefix=settings.API_V1_STR)
app.include_router(review_gates_router, prefix=settings.API_V1_STR)
app.include_router(advisors_router, prefix=settings.API_V1_STR)
app.include_router(system_router, prefix=settings.API_V1_STR)
app.include_router(onboarding_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)


@app.get("/", response_class=HTMLResponse, tags=["Web Dashboard"])
@app.get("/dashboard", response_class=HTMLResponse, tags=["Web Dashboard"])
async def server_dashboard():
    """Interactive Server Dashboard for the Folks Multi-Agent Orchestrator."""
    return HTMLResponse(content=get_dashboard_html())

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

