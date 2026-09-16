import time
from typing import Dict, Any, Callable, Optional
from backend.app.tools.base import ToolResult
from backend.app.tools.registry import tool_registry
from backend.app.security.permissions import permission_manager, PermissionLevel
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.emergency import emergency_manager
from backend.app.database.database import AsyncSessionLocal
from backend.app.database.models import ToolExecutionLog

class ToolExecutor:
    def __init__(self, on_permission_needed: Optional[Callable] = None):
        self.on_permission_needed = on_permission_needed

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        ws_broadcast: Optional[Callable] = None
    ) -> ToolResult:
        if emergency_manager.is_stopped:
            return ToolResult(
                success=False,
                error="Execution blocked: Emergency Stop is currently active."
            )

        tool = tool_registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' is not registered."
            )

        perm_level = tool.permission_level
        approved = True

        # Check if permission escalation is required
        if perm_level in [PermissionLevel.CONFIRM, PermissionLevel.DANGEROUS]:
            action_desc = f"{tool.name} with parameters: {parameters}"
            req = permission_manager.create_request(
                tool_name=tool_name,
                action_summary=action_desc,
                permission_level=perm_level,
                parameters=parameters
            )

            if ws_broadcast:
                await ws_broadcast("assistant.permission_required", {
                    "request_id": req.id,
                    "tool_name": tool_name,
                    "permission_level": perm_level.value,
                    "action_summary": action_desc,
                    "parameters": parameters
                })

            logger.info(f"Awaiting user permission [{perm_level.value}] for {tool_name} (ID: {req.id})")
            approved = await permission_manager.wait_for_approval(req.id, timeout_seconds=120.0)

            if ws_broadcast:
                await ws_broadcast("assistant.permission_resolved", {
                    "request_id": req.id,
                    "approved": approved
                })

        elif perm_level == PermissionLevel.BLOCKED:
            approved = False

        if not approved:
            logger.warning(f"Execution rejected or timed out for {tool_name}")
            return ToolResult(
                success=False,
                error=f"Permission for tool '{tool_name}' was denied or timed out."
            )

        start_time = time.time()
        try:
            logger.info(f"Executing tool: {tool_name}")
            result = await tool.execute(**parameters)
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {str(e)}")
            result = ToolResult(success=False, error=str(e))

        duration_ms = int((time.time() - start_time) * 1000)

        # Log execution to database
        try:
            async with AsyncSessionLocal() as session:
                log_entry = ToolExecutionLog(
                    tool_name=tool_name,
                    parameters=parameters,
                    result={"success": result.success, "message": result.message, "error": result.error},
                    permission_level=perm_level.value,
                    approved=approved,
                    duration_ms=duration_ms
                )
                session.add(log_entry)
                await session.commit()
        except Exception as db_err:
            logger.error(f"Failed to record tool execution log: {str(db_err)}")

        return result

tool_executor = ToolExecutor()
