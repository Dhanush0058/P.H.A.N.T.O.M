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

class SystemPowerControlTool(BaseTool):
    name = "system_power_control"
    description = "Controls computer power states: shutdown laptop/PC, restart, lock screen, sleep mode, or cancel scheduled shutdown."
    category = "System"
    permission_level = PermissionLevel.DANGEROUS
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["shutdown", "restart", "lock", "sleep", "cancel"],
                "description": "Power action to perform: 'shutdown', 'restart', 'lock', 'sleep', or 'cancel'"
            },
            "delay_seconds": {
                "type": "integer",
                "description": "Optional delay in seconds before shutdown/restart (default: 15)"
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str, delay_seconds: int = 15, **kwargs) -> ToolResult:
        res = windows_platform.system_power_action(action, delay_seconds)
        if res.get("success"):
            return ToolResult(success=True, data=res, message=res.get("message"))
        return ToolResult(success=False, error=res.get("error"))
