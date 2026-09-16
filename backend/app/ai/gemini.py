import json
import httpx
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage, AIResponse, ToolCallRequest
from backend.app.core.config import settings
from backend.app.core.logging import logger

class GeminiProvider(AIProvider):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(model_name or settings.AI_MODEL or "gemini-2.0-flash")
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def generate(self, messages: List[AIMessage], system_prompt: Optional[str] = None) -> AIResponse:
        return await self.generate_with_tools(messages, tools=[], system_prompt=system_prompt)

    async def generate_with_tools(
        self,
        messages: List[AIMessage],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        if not self.api_key:
            logger.warning("Gemini API key not found. Please set GEMINI_API_KEY in .env or Settings.")
            return AIResponse(
                content="[JARVIS Notice: Gemini API Key is missing. Please configure GEMINI_API_KEY in the Settings tab.]",
                tool_calls=[]
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        # Convert AIMessages to Gemini contents format
        contents = []
        for msg in messages:
            role = "user" if msg.role == "user" else "model" if msg.role == "assistant" else "user"
            parts = []
            if msg.content:
                parts.append({"text": msg.content})
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    parts.append({
                        "functionCall": {
                            "name": tc.name,
                            "args": tc.arguments
                        }
                    })
            if msg.role == "tool" and msg.tool_call_id:
                parts.append({
                    "functionResponse": {
                        "name": msg.tool_call_id,
                        "response": {"result": msg.content}
                    }
                })
            if parts:
                contents.append({"role": role, "parts": parts})

        # Format function declarations
        gemini_tools = []
        if tools:
            func_decls = []
            for t in tools:
                func_decls.append({
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "parameters": t.get("parameters", {"type": "object", "properties": {}})
                })
            gemini_tools.append({"functionDeclarations": func_decls})

        payload: Dict[str, Any] = {"contents": contents}
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        if gemini_tools:
            payload["tools"] = gemini_tools

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()

            candidates = data.get("candidates", [])
            if not candidates:
                return AIResponse(content="No response generated.", tool_calls=[])

            candidate = candidates[0]
            content_parts = candidate.get("content", {}).get("parts", [])
            text_chunks = []
            tool_calls = []

            for part in content_parts:
                if "text" in part:
                    text_chunks.append(part["text"])
                if "functionCall" in part:
                    fc = part["functionCall"]
                    tool_calls.append(ToolCallRequest(
                        id=fc.get("name", "call"),
                        name=fc.get("name", ""),
                        arguments=fc.get("args", {})
                    ))

            usage = data.get("usageMetadata", {})
            tokens = usage.get("totalTokenCount", 0)

            return AIResponse(
                content="".join(text_chunks),
                tool_calls=tool_calls,
                tokens_used=tokens,
                raw_response=data
            )
        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            return AIResponse(
                content=f"Error connecting to Gemini AI: {str(e)}",
                tool_calls=[]
            )
