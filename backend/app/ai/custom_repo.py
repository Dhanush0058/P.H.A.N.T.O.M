import json
import httpx
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage, AIResponse, ToolCallRequest
from backend.app.core.config import settings
from backend.app.core.logging import logger

class CustomRepoLLMProvider(AIProvider):
    """
    Dedicated Provider for integrating user's custom multi-model LLM repository (1.47B token pool / model switching).
    Supports standard OpenAI-compatible and custom routing endpoints.
    """
    def __init__(self, model_name: Optional[str] = None, api_url: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(model_name or "custom-router-model")
        self.api_url = (api_url or settings.CUSTOM_LLM_API_URL or "http://localhost:8080/v1").rstrip("/")
        self.api_key = api_key or settings.CUSTOM_LLM_API_KEY or "local-secret"

    async def generate(self, messages: List[AIMessage], system_prompt: Optional[str] = None) -> AIResponse:
        return await self.generate_with_tools(messages, tools=[], system_prompt=system_prompt)

    async def generate_with_tools(
        self,
        messages: List[AIMessage],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for m in messages:
            formatted.append({"role": m.role, "content": m.content or ""})

        payload = {
            "model": self.model_name,
            "messages": formatted,
            "tools": tools,
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(f"{self.api_url}/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choice = data["choices"][0]["message"]
                    tool_calls = []
                    if "tool_calls" in choice and choice["tool_calls"]:
                        for tc in choice["tool_calls"]:
                            args = tc["function"].get("arguments", {})
                            if isinstance(args, str):
                                try:
                                    args = json.loads(args)
                                except Exception:
                                    args = {}
                            tool_calls.append(ToolCallRequest(
                                id=tc.get("id", "call"),
                                name=tc["function"]["name"],
                                arguments=args
                            ))
                    return AIResponse(
                        content=choice.get("content") or "",
                        tool_calls=tool_calls,
                        tokens_used=data.get("usage", {}).get("total_tokens", 0),
                        raw_response=data
                    )
                else:
                    return AIResponse(
                        content=f"Custom LLM Repo returned status {res.status_code}: {res.text}",
                        tool_calls=[]
                    )
        except Exception as e:
            logger.error(f"Custom LLM Repo connection error: {str(e)}")
            return AIResponse(
                content=f"Unable to connect to Custom LLM Service at {self.api_url}: {str(e)}",
                tool_calls=[]
            )
