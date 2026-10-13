import argparse
import asyncio
import logging
from .client import DaemonWebSocketClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("folks.daemon.main")

async def run_daemon(server_ws_url: str, daemon_id: str, working_dir: str):
    client = DaemonWebSocketClient(server_ws_url=server_ws_url, daemon_id=daemon_id, working_dir=working_dir)
    await client.connect()

    logger.info("Daemon runner active. Listening for commands and keeping heartbeat alive...")
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Daemon runner stopping...")
    finally:
        await client.disconnect()

def main():
    parser = argparse.ArgumentParser(description="Folks Local Host CLI Execution Daemon")
    parser.add_argument("--server", default="ws://127.0.0.1:8000", help="Orchestrator WebSocket URL")
    parser.add_argument("--id", default=None, help="Daemon identifier")
    parser.add_argument("--dir", default=None, help="Working directory for task executions")
    args = parser.parse_args()

    try:
        asyncio.run(run_daemon(args.server, args.id, args.dir))
    except KeyboardInterrupt:
        logger.info("Daemon stopped by user.")

if __name__ == "__main__":
    main()
