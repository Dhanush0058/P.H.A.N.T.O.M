from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.platform.windows import windows_platform

class GetSystemStatusTool(BaseTool):
    name = "get_system_status"
    description = "Retrieves live computer metrics including CPU, RAM, Disk, Network, and Battery status."
    category = "System"
    permission_level = PermissionLevel.SAFE
    parameters = {"type": "object", "properties": {}}

    async def execute(self, **kwargs) -> ToolResult:
        metrics = windows_platform.get_system_metrics()
        return ToolResult(
            success=True,
            data=metrics,
            message=f"CPU: {metrics['cpu']['usage_percent']}%, RAM: {metrics['memory']['percent']}%, Disk: {metrics['disk']['percent']}%"
        )

class GetProcessesTool(BaseTool):
    name = "get_processes"
    description = "Retrieves a list of active top memory and CPU consuming processes."
    category = "System"
    permission_level = PermissionLevel.SAFE
    parameters = {"type": "object", "properties": {}}

    async def execute(self, **kwargs) -> ToolResult:
        procs = windows_platform.get_running_processes()
        return ToolResult(
            success=True,
            data={"processes": procs},
            message=f"Retrieved {len(procs)} active processes"
        )
