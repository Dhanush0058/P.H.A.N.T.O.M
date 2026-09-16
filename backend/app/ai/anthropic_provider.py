import json
import httpx
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage, AIResponse, ToolCallRequest
from backend.app.core.config import settings
from backend.app.core.logging import logger

class AnthropicProvider(AIProvider):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(model_name or "claude-3-5-sonnet-20241022")
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

    async def generate(self, messages: List[AIMessage], system_prompt: Optional[str] = None) -> AIResponse:
        return await self.generate_with_tools(messages, tools=[], system_prompt=system_prompt)

    async def generate_with_tools(
        self,
        messages: List[AIMessage],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        if not self.api_key:
            return AIResponse(
                content="[JARVIS Notice: Anthropic API Key is missing. Please configure ANTHROPIC_API_KEY in Settings.]",
                tool_calls=[]
            )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        formatted_messages = []
        for msg in messages:
            if msg.role in ["user", "assistant"]:
                formatted_messages.append({"role": msg.role, "content": msg.content or ""})

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "max_tokens": 4096,
            "messages": formatted_messages
        }
        if system_prompt:
            payload["system"] = system_prompt

        if tools:
            anthropic_tools = []
            for t in tools:
                anthropic_tools.append({
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "input_schema": t.get("parameters", {"type": "object", "properties": {}})
                })
            payload["tools"] = anthropic_tools

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()

            content_blocks = data.get("content", [])
            text_chunks = []
            tool_calls = []

            for block in content_blocks:
                if block.get("type") == "text":
                    text_chunks.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_calls.append(ToolCallRequest(
                        id=block.get("id", ""),
                        name=block.get("name", ""),
                        arguments=block.get("input", {})
                    ))

            usage = data.get("usage", {})
            tokens = (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)

            return AIResponse(
                content="".join(text_chunks),
                tool_calls=tool_calls,
                tokens_used=tokens,
                raw_response=data
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return AIResponse(content=f"Error connecting to Anthropic: {str(e)}", tool_calls=[])
