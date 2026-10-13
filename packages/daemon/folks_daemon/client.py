import asyncio
import json
import logging
import uuid
from typing import Optional
import websockets
from .executor import HostCLIExecutor

logger = logging.getLogger("folks.daemon")

class DaemonWebSocketClient:
    def __init__(
        self,
        server_ws_url: str,
        daemon_id: Optional[str] = None,
        working_dir: Optional[str] = None,
        heartbeat_interval: int = 15
    ):
        self.server_ws_url = server_ws_url.rstrip("/")
        self.daemon_id = daemon_id or f"daemon-host-{uuid.uuid4().hex[:8]}"
        self.executor = HostCLIExecutor(working_dir)
        self.heartbeat_interval = heartbeat_interval
        
        self.active_task_id: Optional[str] = None
        self.active_correlation_id: Optional[str] = None
        self.ws = None
        self._running = False
        self._heartbeat_task = None

    async def connect(self):
        url = f"{self.server_ws_url}/ws/daemon/{self.daemon_id}"
        logger.info(f"Connecting Execution Daemon to {url}...")
        self.ws = await websockets.connect(url)
        self._running = True
        logger.info(f"Connected to Orchestrator as Daemon '{self.daemon_id}'.")
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        while self._running:
            try:
                if self.ws and self.active_task_id:
                    ping_msg = {
                        "type": "heartbeat",
                        "daemon_id": self.daemon_id,
                        "task_id": self.active_task_id,
                        "correlation_id": self.active_correlation_id or "daemon-ping"
                    }
                    await self.ws.send(json.dumps(ping_msg))
                    logger.debug(f"Heartbeat emitted for active Task {self.active_task_id}")
            except Exception as e:
                logger.error(f"Failed to send heartbeat: {e}")
            await asyncio.sleep(self.heartbeat_interval)

    async def execute_task_command(self, task_id: str, correlation_id: str, command: str):
        self.active_task_id = task_id
        self.active_correlation_id = correlation_id
        logger.info(f"[corr_id: {correlation_id}] Executing: {command}")

        try:
            async for stream_name, chunk in self.executor.execute_command_stream(
                command, correlation_id, task_id
            ):
                if self.ws:
                    stream_msg = {
                        "type": "terminal_stream",
                        "task_id": task_id,
                        "correlation_id": correlation_id,
                        "stream": stream_name,
                        "text": chunk
                    }
                    await self.ws.send(json.dumps(stream_msg))
        finally:
            self.active_task_id = None
            self.active_correlation_id = None

    async def disconnect(self):
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self.ws:
            await self.ws.close()
            logger.info("Daemon disconnected cleanly.")
