import asyncio
import os
import sys
from typing import AsyncGenerator, Tuple, Optional

class HostCLIExecutor:
    def __init__(self, working_dir: Optional[str] = None):
        self.working_dir = working_dir or os.getcwd()

    async def execute_command_stream(
        self,
        command: str,
        correlation_id: str,
        task_id: str
    ) -> AsyncGenerator[Tuple[str, str], None]:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.working_dir
        )

        while True:
            stdout_line = await proc.stdout.readline() if proc.stdout else b""
            if stdout_line:
                yield ("stdout", stdout_line.decode("utf-8", errors="replace"))

            stderr_line = await proc.stderr.readline() if proc.stderr else b""
            if stderr_line:
                yield ("stderr", stderr_line.decode("utf-8", errors="replace"))

            if not stdout_line and not stderr_line and proc.returncode is not None:
                break
            
            if proc.stdout.at_eof() and proc.stderr.at_eof():
                await proc.wait()
                break

    async def get_git_diff(self) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                "git diff",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir
            )
            stdout, _ = await proc.communicate()
            return stdout.decode("utf-8", errors="replace")
        except Exception:
            return ""
