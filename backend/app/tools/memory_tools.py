from typing import Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.memory.manager import memory_manager

class RememberTool(BaseTool):
    name = "remember"
    description = "Saves a fact, preference, or context into long-term memory for future recall."
    category = "Memory"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Memory identifier or key (e.g., 'main_project', 'favorite_editor')"},
            "value": {"type": "string", "description": "Information/fact to remember"},
            "memory_type": {"type": "string", "enum": ["preference", "fact", "goal", "context"], "description": "Type of memory"}
        },
        "required": ["key", "value"]
    }

    async def execute(self, key: str, value: str, memory_type: str = "fact", **kwargs) -> ToolResult:
        try:
            res = await memory_manager.long_term.remember(key, value, memory_type=memory_type)
            return ToolResult(success=True, data=res, message=f"Remembered: '{key}' = '{value}'")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class RecallTool(BaseTool):
    name = "recall"
    description = "Retrieves a stored fact or preference from long-term memory by key."
    category = "Memory"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Memory key to search"}
        },
        "required": ["key"]
    }

    async def execute(self, key: str, **kwargs) -> ToolResult:
        try:
            res = await memory_manager.long_term.recall(key)
            if res:
                return ToolResult(success=True, data=res, message=f"Recalled: '{key}' = '{res['value']}'")
            return ToolResult(success=False, error=f"No memory found for '{key}'.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class ForgetTool(BaseTool):
    name = "forget"
    description = "Deletes a stored memory item by key."
    category = "Memory"
    permission_level = PermissionLevel.CONFIRM
    parameters = {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Memory key to forget"}
        },
        "required": ["key"]
    }

    async def execute(self, key: str, **kwargs) -> ToolResult:
        try:
            res = await memory_manager.long_term.forget(key)
            if res:
                return ToolResult(success=True, data={"key": key}, message=f"Forgotten memory '{key}'.")
            return ToolResult(success=False, error=f"Memory '{key}' was not found.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class SearchMemoryTool(BaseTool):
    name = "search_memory"
    description = "Searches across all long-term memories for keywords or concepts."
    category = "Memory"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Keyword to query in memory"}
        }
    }

    async def execute(self, query: str = "", **kwargs) -> ToolResult:
        try:
            res = await memory_manager.long_term.search(query)
            return ToolResult(success=True, data={"memories": res}, message=f"Found {len(res)} memories")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
