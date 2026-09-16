from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict
from datetime import datetime

class AssistantState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    EXECUTING = "EXECUTING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"

class WebSocketEventType(str, Enum):
    STATE_CHANGE = "assistant.state_change"
    LISTENING = "assistant.listening"
    THINKING = "assistant.thinking"
    PLAN_UPDATE = "assistant.plan_update"
    TOOL_CALL = "assistant.tool_call"
    TOOL_RESULT = "assistant.tool_result"
    PERMISSION_REQUIRED = "assistant.permission_required"
    PERMISSION_RESOLVED = "assistant.permission_resolved"
    SPEAKING = "assistant.speaking"
    AUDIO_CHUNK = "assistant.audio_chunk"
    CHAT_MESSAGE = "assistant.chat_message"
    SYSTEM_STATS = "assistant.system_stats"
    EMERGENCY_STOP = "assistant.emergency_stop"
    ERROR = "assistant.error"

class WebSocketEvent(BaseModel):
    event: WebSocketEventType
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
