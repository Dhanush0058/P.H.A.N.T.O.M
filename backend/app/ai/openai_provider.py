import json
import httpx
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage, AIResponse, ToolCallRequest
from backend.app.core.config import settings
from backend.app.core.logging import logger

class OpenAIProvider(AIProvider):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(model_name or "gpt-4o")
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = (base_url or settings.OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")

    async def generate(self, messages: List[AIMessage], system_prompt: Optional[str] = None) -> AIResponse:
        return await self.generate_with_tools(messages, tools=[], system_prompt=system_prompt)

    async def generate_with_tools(
        self,
        messages: List[AIMessage],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            item: Dict[str, Any] = {"role": msg.role, "content": msg.content or ""}
            if msg.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}
                    }
                    for tc in msg.tool_calls
                ]
            if msg.role == "tool" and msg.tool_call_id:
                item["tool_call_id"] = msg.tool_call_id
            formatted_messages.append(item)

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": 0.2
        }

        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.get("name"),
                        "description": t.get("description", ""),
                        "parameters": t.get("parameters", {"type": "object", "properties": {}})
                    }
                }
                for t in tools
            ]
            payload["tool_choice"] = "auto"

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()

            choice = data["choices"][0]["message"]
            content = choice.get("content") or ""
            tool_calls = []

            if "tool_calls" in choice and choice["tool_calls"]:
                for tc in choice["tool_calls"]:
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except Exception:
                        args = {}
                    tool_calls.append(ToolCallRequest(
                        id=tc.get("id", ""),
                        name=tc["function"]["name"],
                        arguments=args
                    ))

            usage = data.get("usage", {})
            tokens = usage.get("total_tokens", 0)

            return AIResponse(
                content=content,
                tool_calls=tool_calls,
                tokens_used=tokens,
                raw_response=data
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return AIResponse(
                content=f"Error connecting to OpenAI-compatible provider: {str(e)}",
                tool_calls=[]
            )
