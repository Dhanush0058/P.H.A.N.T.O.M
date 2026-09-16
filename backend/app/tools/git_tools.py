import asyncio
from typing import Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.core.config import settings

async def _run_git(args: list[str], cwd: Optional[str] = None) -> ToolResult:
    work_dir = cwd or settings.WORKSPACE_ROOT
    try:
        proc = await asyncio.create_subprocess_exec(
            "git", *args,
            cwd=work_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15.0)
        out = stdout.decode("utf-8", errors="replace").strip()
        err = stderr.decode("utf-8", errors="replace").strip()
        if proc.returncode == 0:
            return ToolResult(success=True, data={"output": out}, message=out or "Success")
        return ToolResult(success=False, error=err or out or "Git command failed")
    except Exception as e:
        return ToolResult(success=False, error=str(e))

class GitStatusTool(BaseTool):
    name = "git_status"
    description = "Checks the git working tree status (modified, staged, untracked files)."
    category = "Git"
    permission_level = PermissionLevel.SAFE
    parameters = {"type": "object", "properties": {}}

    async def execute(self, **kwargs) -> ToolResult:
        return await _run_git(["status", "--short"])

class GitDiffTool(BaseTool):
    name = "git_diff"
    description = "Shows unstaged or staged changes in the git repository."
    category = "Git"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "staged": {"type": "boolean", "description": "View staged diff (--cached)"}
        }
    }

    async def execute(self, staged: bool = False, **kwargs) -> ToolResult:
        args = ["diff", "--cached"] if staged else ["diff"]
        return await _run_git(args)

class GitLogTool(BaseTool):
    name = "git_log"
    description = "Shows recent commit logs in the git repository."
    category = "Git"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "max_commits": {"type": "integer", "description": "Number of commits to retrieve (default 10)"}
        }
    }

    async def execute(self, max_commits: int = 10, **kwargs) -> ToolResult:
        return await _run_git(["log", f"-n{max_commits}", "--oneline"])

class GitBranchTool(BaseTool):
    name = "git_branch"
    description = "Lists git branches and active branch."
    category = "Git"
    permission_level = PermissionLevel.SAFE
    parameters = {"type": "object", "properties": {}}

    async def execute(self, **kwargs) -> ToolResult:
        return await _run_git(["branch", "-a"])
