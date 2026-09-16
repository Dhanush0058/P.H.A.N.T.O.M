from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncGenerator

class ToolCallRequest(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]

class AIMessage(BaseModel):
    role: str  # user, assistant, system, tool
    content: Optional[str] = ""
    tool_calls: Optional[List[ToolCallRequest]] = None
    tool_call_id: Optional[str] = None

class AIResponse(BaseModel):
    content: str
    tool_calls: List[ToolCallRequest] = Field(default_factory=list)
    raw_response: Optional[Any] = None
    finish_reason: Optional[str] = None
    tokens_used: Optional[int] = None

class AIProvider(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    async def generate(self, messages: List[AIMessage], system_prompt: Optional[str] = None) -> AIResponse:
        pass

    @abstractmethod
    async def generate_with_tools(
        self,
        messages: List[AIMessage],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        pass

    async def generate_stream(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        # Default non-streaming fallback
        resp = await self.generate(messages, system_prompt)
        yield resp.content
