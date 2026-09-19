from typing import Dict, List, Optional
from backend.app.tools.base import BaseTool
from backend.app.tools.computer import (
    OpenApplicationTool,
    CloseApplicationTool,
    TakeScreenshotTool,
    MouseControlTool,
    KeyboardControlTool,
    SendWhatsAppMessageTool,
    TypeAndPressEnterTool
)
from backend.app.tools.filesystem import (
    ListFilesTool,
    ReadFileTool,
    WriteFileTool,
    DeleteFileTool
)
from backend.app.tools.terminal import RunCommandTool
from backend.app.tools.browser import (
    OpenBrowserTool,
    SearchWebTool,
    GetPageContentTool
)
from backend.app.tools.git_tools import (
    GitStatusTool,
    GitDiffTool,
    GitLogTool,
    GitBranchTool
)
from backend.app.tools.github_tools import (
    GitHubSearchReposTool,
    GitHubCreateIssueTool
)
from backend.app.tools.memory_tools import (
    RememberTool,
    RecallTool,
    ForgetTool,
    SearchMemoryTool
)
from backend.app.tools.system_tools import (
    GetSystemStatusTool,
    GetProcessesTool,
    SystemPowerControlTool
)
from backend.app.core.logging import logger

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name} [{tool.category}]")

    TOOL_ALIASES = {
        "open_whatsapp_message": "send_whatsapp_message",
        "whatsapp_message": "send_whatsapp_message",
        "send_message": "send_whatsapp_message",
        "whatsapp": "send_whatsapp_message",
        "open_app": "open_application",
        "launch_app": "open_application",
        "launch_application": "open_application",
        "screenshot": "take_screenshot",
        "capture_screen": "take_screenshot",
        "type_text": "type_and_press_enter",
        "exec_command": "run_command",
        "execute_command": "run_command",
        "search": "search_web",
        "open_url": "open_browser",
        "shutdown": "system_power_control",
        "shutdown_laptop": "system_power_control",
        "power_off": "system_power_control",
        "poweroff": "system_power_control",
        "restart": "system_power_control",
        "reboot": "system_power_control",
        "lock": "system_power_control",
        "lock_screen": "system_power_control",
        "sleep": "system_power_control"
    }

    def get_tool(self, name: str) -> Optional[BaseTool]:
        clean_name = name.lower().strip()
        canonical_name = self.TOOL_ALIASES.get(clean_name, clean_name)
        tool = self._tools.get(canonical_name)
        if tool:
            return tool
        
        # Suffix / prefix fuzzy search
        for k, v in self._tools.items():
            if clean_name in k or k in clean_name:
                return v
        return None

    def list_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_tool_schemas(self) -> List[Dict]:
        return [tool.to_dict() for tool in self._tools.values()]

    def _register_default_tools(self):
        # Computer
        self.register(OpenApplicationTool())
        self.register(CloseApplicationTool())
        self.register(TakeScreenshotTool())
        self.register(MouseControlTool())
        self.register(KeyboardControlTool())
        self.register(SendWhatsAppMessageTool())
        self.register(TypeAndPressEnterTool())

        # Filesystem
        self.register(ListFilesTool())
        self.register(ReadFileTool())
        self.register(WriteFileTool())
        self.register(DeleteFileTool())

        # Terminal
        self.register(RunCommandTool())

        # Browser / Web
        self.register(OpenBrowserTool())
        self.register(SearchWebTool())
        self.register(GetPageContentTool())

        # Git
        self.register(GitStatusTool())
        self.register(GitDiffTool())
        self.register(GitLogTool())
        self.register(GitBranchTool())

        # GitHub
        self.register(GitHubSearchReposTool())
        self.register(GitHubCreateIssueTool())

        # Memory
        self.register(RememberTool())
        self.register(RecallTool())
        self.register(ForgetTool())
        self.register(SearchMemoryTool())

        # System
        self.register(GetSystemStatusTool())
        self.register(GetProcessesTool())
        self.register(SystemPowerControlTool())

tool_registry = ToolRegistry()
