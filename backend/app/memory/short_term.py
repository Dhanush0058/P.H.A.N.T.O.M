from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.ai.base import AIMessage

class ShortTermMemory:
    """Manages active conversation window and rolling turn history."""
    def __init__(self, max_turns: int = 25):
        self.max_turns = max_turns
        self.messages: List[AIMessage] = []

    def add_message(self, role: str, content: str, tool_calls: Optional[List[Any]] = None, tool_call_id: Optional[str] = None):
        msg = AIMessage(role=role, content=content, tool_calls=tool_calls, tool_call_id=tool_call_id)
        self.messages.append(msg)
        if len(self.messages) > self.max_turns * 2:
            # Retain system / recent messages
            self.messages = self.messages[-(self.max_turns * 2):]

    def get_messages(self) -> List[AIMessage]:
        return list(self.messages)

    def clear(self):
        self.messages.clear()

class WorkingMemory:
    """Manages current task breakdown, intermediate tool observations, and scratchpad."""
    def __init__(self):
        self.current_goal: Optional[str] = None
        self.steps: List[Dict[str, Any]] = []
        self.scratchpad: Dict[str, Any] = {}

    def set_goal(self, goal: str):
        self.current_goal = goal
        self.steps.clear()
        self.scratchpad.clear()

    def add_step(self, step_name: str, status: str = "pending", details: Optional[str] = None):
        self.steps.append({
            "step": step_name,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })

    def update_step(self, step_idx: int, status: str, details: Optional[str] = None):
        if 0 <= step_idx < len(self.steps):
            self.steps[step_idx]["status"] = status
            if details:
                self.steps[step_idx]["details"] = details

    def set_scratchpad(self, key: str, value: Any):
        self.scratchpad[key] = value

    def get_context_summary(self) -> str:
        if not self.current_goal:
            return ""
        lines = [f"Current Goal: {self.current_goal}"]
        for i, s in enumerate(self.steps, 1):
            lines.append(f"  Step {i} [{s['status']}]: {s['step']}")
        return "\n".join(lines)
