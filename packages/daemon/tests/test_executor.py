import pytest
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.daemon.folks_daemon.executor import HostCLIExecutor

@pytest.mark.asyncio
async def test_host_cli_executor_stdout_and_stderr():
    executor = HostCLIExecutor()

    # 1. Test stdout streaming
    cmd_stdout = f'"{sys.executable}" -c "print(\'daemon-worker-active\')"'
    chunks_stdout = []
    async for stream_name, chunk in executor.execute_command_stream(
        command=cmd_stdout,
        correlation_id="corr-daemon-test-1",
        task_id="task-test-1"
    ):
        chunks_stdout.append((stream_name, chunk))

    assert any(name == "stdout" and "daemon-worker-active" in text for name, text in chunks_stdout)

    # 2. Test stderr streaming
    cmd_stderr = f'"{sys.executable}" -c "import sys; sys.stderr.write(\'fatal-warning-check\\n\')"'
    chunks_stderr = []
    async for stream_name, chunk in executor.execute_command_stream(
        command=cmd_stderr,
        correlation_id="corr-daemon-test-2",
        task_id="task-test-2"
    ):
        chunks_stderr.append((stream_name, chunk))

    assert any(name == "stderr" and "fatal-warning-check" in text for name, text in chunks_stderr)
