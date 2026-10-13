import json
import logging
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.reaper import LockReaper
from packages.db_schema.models import AuditLog

logger = logging.getLogger("folks.ws")

router = APIRouter(prefix="/ws", tags=["Real-Time WebSockets"])

class ConnectionManager:
    def __init__(self):
        self.active_cockpits: Set[WebSocket] = set()
        self.active_daemons: Dict[str, WebSocket] = {}

    async def connect_cockpit(self, websocket: WebSocket):
        await websocket.accept()
        self.active_cockpits.add(websocket)
        logger.info("Cockpit UI client connected to WebSocket.")

    def disconnect_cockpit(self, websocket: WebSocket):
        self.active_cockpits.discard(websocket)
        logger.info("Cockpit UI client disconnected.")

    async def broadcast_cockpit(self, message: dict):
        dead_sockets = set()
        for ws in self.active_cockpits:
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.add(ws)
        self.active_cockpits -= dead_sockets

    async def connect_daemon(self, daemon_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_daemons[daemon_id] = websocket
        logger.info(f"Execution Daemon '{daemon_id}' connected to WebSocket.")

    def disconnect_daemon(self, daemon_id: str):
        if daemon_id in self.active_daemons:
            del self.active_daemons[daemon_id]
        logger.info(f"Execution Daemon '{daemon_id}' disconnected.")

ws_manager = ConnectionManager()


@router.websocket("/cockpit")
async def cockpit_ws_endpoint(websocket: WebSocket):
    await ws_manager.connect_cockpit(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_cockpit(websocket)


@router.websocket("/daemon/{daemon_id}")
async def daemon_ws_endpoint(daemon_id: str, websocket: WebSocket):
    await ws_manager.connect_daemon(daemon_id, websocket)
    try:
        while True:
            text_data = await websocket.receive_text()
            try:
                msg = json.loads(text_data)
            except Exception:
                continue

            msg_type = msg.get("type")

            if msg_type == "heartbeat":
                task_id = msg.get("task_id")
                corr_id = msg.get("correlation_id", "daemon-heartbeat")
                if task_id:
                    async with AsyncSessionLocal() as db:
                        renewed = await LockReaper.renew_heartbeat(
                            db=db,
                            task_id=task_id,
                            daemon_id=daemon_id,
                            correlation_id=corr_id
                        )
                        if renewed:
                            await db.commit()
                        await websocket.send_json({
                            "type": "heartbeat_ack",
                            "task_id": task_id,
                            "renewed": renewed
                        })

            elif msg_type == "terminal_stream":
                task_id = msg.get("task_id")
                corr_id = msg.get("correlation_id", "terminal-stream")
                stream = msg.get("stream", "stdout")
                text = msg.get("text", "")

                await ws_manager.broadcast_cockpit({
                    "type": "terminal_chunk",
                    "task_id": task_id,
                    "correlation_id": corr_id,
                    "daemon_id": daemon_id,
                    "stream": stream,
                    "text": text
                })

                if stream == "stderr":
                    async with AsyncSessionLocal() as db:
                        audit = AuditLog(
                            correlation_id=corr_id,
                            task_id=task_id,
                            daemon_id=daemon_id,
                            event_type="DAEMON_STDERR",
                            level="WARN",
                            message=text[:500],
                            payload={"stream": "stderr", "full_chunk_len": len(text)}
                        )
                        db.add(audit)
                        await db.commit()

            elif msg_type == "task_status_update":
                await ws_manager.broadcast_cockpit({
                    "type": "task_status_changed",
                    "daemon_id": daemon_id,
                    "payload": msg
                })

    except WebSocketDisconnect:
        ws_manager.disconnect_daemon(daemon_id)
