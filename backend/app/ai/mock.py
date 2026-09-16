import uuid
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage, AIResponse, ToolCallRequest

class MockAIProvider(AIProvider):
    def __init__(self, model_name: str = "mock-jarvis-v1"):
        super().__init__(model_name)

    async def generate(self, messages: List[AIMessage], system_prompt: Optional[str] = None) -> AIResponse:
        last_msg = messages[-1].content if messages else ""
        content = f"Mock response to: '{last_msg}'. JARVIS core is operational."
        return AIResponse(content=content, tokens_used=15)

    async def generate_with_tools(
        self,
        messages: List[AIMessage],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        last_msg = (messages[-1].content or "").lower() if messages else ""

        # Smart mock heuristic for unit testing tool invocation
        if "open vs code" in last_msg or "open vscode" in last_msg:
            return AIResponse(
                content="Opening VS Code for you.",
                tool_calls=[ToolCallRequest(
                    id=str(uuid.uuid4())[:8],
                    name="open_application",
                    arguments={"app_name": "vscode"}
                )],
                tokens_used=24
            )
        elif "system status" in last_msg or "status" in last_msg:
            return AIResponse(
                content="Checking system hardware telemetry.",
                tool_calls=[ToolCallRequest(
                    id=str(uuid.uuid4())[:8],
                    name="get_system_status",
                    arguments={}
                )],
                tokens_used=20
            )
        elif "remember that" in last_msg:
            # extract key/val
            parts = last_msg.replace("remember that", "").strip()
            return AIResponse(
                content="Saving preference to long-term memory.",
                tool_calls=[ToolCallRequest(
                    id=str(uuid.uuid4())[:8],
                    name="remember",
                    arguments={"key": "user_fact", "value": parts, "memory_type": "preference"}
                )],
                tokens_used=28
            )
        elif "search" in last_msg:
            return AIResponse(
                content="Searching web...",
                tool_calls=[ToolCallRequest(
                    id=str(uuid.uuid4())[:8],
                    name="search_web",
                    arguments={"query": last_msg.replace("search", "").strip()}
                )],
                tokens_used=25
            )

        return AIResponse(
            content=f"Understood. Operating as JARVIS. Processed query: '{messages[-1].content}'.",
            tool_calls=[],
            tokens_used=18
        )
