import asyncio
import subprocess
from typing import Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.security.validator import command_validator
from backend.app.core.config import settings
from backend.app.core.logging import logger

class RunCommandTool(BaseTool):
    name = "run_command"
    description = "Executes a shell or terminal command in the workspace."
    category = "Terminal"
    permission_level = PermissionLevel.CONFIRM
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to run (e.g., 'python --version', 'git status', 'pip install <pkg>')"},
            "cwd": {"type": "string", "description": "Working directory path"}
        },
        "required": ["command"]
    }

    async def execute(self, command: str, cwd: Optional[str] = None, **kwargs) -> ToolResult:
        if not settings.ALLOW_TERMINAL:
            return ToolResult(success=False, error="Terminal execution is disabled in settings.")

        # Classify command
        perm_level, reason = command_validator.classify_command(command)
        if perm_level == PermissionLevel.BLOCKED:
            return ToolResult(success=False, error=f"SECURITY BLOCK: {reason}")

        work_dir = cwd or settings.WORKSPACE_ROOT
        try:
            logger.info(f"Executing terminal command: '{command}' in '{work_dir}'")
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=45.0)
            except asyncio.TimeoutError:
                proc.kill()
                return ToolResult(success=False, error="Command execution timed out after 45 seconds.")

            out_text = stdout.decode("utf-8", errors="replace").strip()
            err_text = stderr.decode("utf-8", errors="replace").strip()

            success = proc.returncode == 0
            return ToolResult(
                success=success,
                data={
                    "command": command,
                    "returncode": proc.returncode,
                    "stdout": out_text,
                    "stderr": err_text
                },
                message=f"Command finished with code {proc.returncode}"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
