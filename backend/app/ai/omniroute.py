import json
import re
import httpx
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage, AIResponse, ToolCallRequest
from backend.app.core.config import settings
from backend.app.core.logging import logger

TOOL_SYSTEM_INSTRUCTION = """
You have access to the following tools:
{tool_descriptions}

CRITICAL RULES:
1. To invoke a tool, output a JSON block in this exact format:
```json
{{
  "tool_call": {{
    "name": "tool_name",
    "arguments": {{
      "arg1": "value1"
    }}
  }}
}}
```
2. IMPORTANT: If a tool has already been executed (see the tool output in the conversation), DO NOT call the tool again. Immediately respond to the user with a natural language confirmation.
"""

class OmniRouteProvider(AIProvider):
    """
    OmniRoute AI Gateway Provider.
    Routes queries through 352 AI providers (~1.51B free tokens/mo pool)
    using auto-combos with prompt-safe function calling fallback.
    """
    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        super().__init__(model_name or settings.OMNIROUTE_MODEL or "auto")
        self.base_url = (base_url or settings.OMNIROUTE_BASE_URL or "http://localhost:20128/v1").rstrip("/")
        self.api_key = api_key or settings.OMNIROUTE_API_KEY or "omniroute-free-key"

    async def check_health(self) -> Dict[str, Any]:
        """Check if local OmniRoute gateway is running on localhost:20128."""
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/models")
                if res.status_code == 200:
                    models = res.json().get("data", [])
                    return {"online": True, "models_count": len(models), "base_url": self.base_url}
        except Exception as e:
            return {"online": False, "error": str(e), "base_url": self.base_url}
        return {"online": False, "base_url": self.base_url}

    async def generate(self, messages: List[AIMessage], system_prompt: Optional[str] = None) -> AIResponse:
        return await self._call_gateway(messages, system_prompt=system_prompt, tools=None)

    async def generate_with_tools(
        self,
        messages: List[AIMessage],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        # Build tool description prompt for resilient multi-model tool calling
        tools_desc = []
        if tools:
            for t in tools:
                tools_desc.append(f"- {t.get('name')}: {t.get('description')}. Parameters: {json.dumps(t.get('parameters', {}))}")
            tools_text = "\n".join(tools_desc)
            augmented_system = (system_prompt or "") + "\n\n" + TOOL_SYSTEM_INSTRUCTION.format(tool_descriptions=tools_text)
        else:
            augmented_system = system_prompt

        # Attempt call (without raw tools parameter to avoid 503 on models lacking native schema support)
        resp = await self._call_gateway(messages, system_prompt=augmented_system, tools=None)

        # Parse potential JSON tool call from model text
        parsed_calls = self._extract_tool_calls_from_text(resp.content)
        if parsed_calls:
            resp.tool_calls.extend(parsed_calls)

        return resp

    def _extract_tool_calls_from_text(self, text: str) -> List[ToolCallRequest]:
        calls = []
        # Look for ```json { "tool_call": ... } ``` or raw JSON
        match = re.search(r'```(?:json)?\s*(\{\s*"tool_call"\s*:\s*\{.*?\}\s*\})\s*```', text, re.DOTALL)
        raw_json_str = match.group(1) if match else None

        if not raw_json_str:
            match_raw = re.search(r'(\{\s*"tool_call"\s*:\s*\{\s*"name"\s*:\s*"[^"]+".*?\}\s*\})', text, re.DOTALL)
            if match_raw:
                raw_json_str = match_raw.group(1)

        if raw_json_str:
            try:
                data = json.loads(raw_json_str)
                tc = data.get("tool_call", {})
                name = tc.get("name")
                args = tc.get("arguments", {})
                if name:
                    calls.append(ToolCallRequest(
                        id=f"call_{name}",
                        name=name,
                        arguments=args
                    ))
            except Exception:
                pass
        return calls

    async def _call_gateway(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AIResponse:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            item: Dict[str, Any] = {"role": msg.role, "content": msg.content or ""}
            formatted_messages.append(item)

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": 0.2,
            "stream": False
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            timeout_cfg = httpx.Timeout(60.0, connect=3.0)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if res.status_code != 200:
                    logger.error(f"OmniRoute error status {res.status_code}: {res.text}")
                    if "Maximum combo retry limit reached" in res.text or "exhausted_connection" in res.text or res.status_code == 503:
                        return AIResponse(
                            content=(
                                "⚠️ **OmniRoute Public Scraper Pool Exhausted (Status 503)**\n\n"
                                "OmniRoute attempted to route your prompt across 27 public keyless web scrapers, but those endpoints are currently rate-limited by upstream web services.\n\n"
                                "### 🚀 How to fix this in 30 seconds:\n"
                                "1. Open the OmniRoute dashboard in your browser: [http://localhost:20128](http://localhost:20128)\n"
                                "2. Go to **Connections** / **Add Provider** and paste any free provider key (e.g., **Groq**, **Google AI Studio / Gemini**, **Mistral**, or **GitHub Token**).\n"
                                "3. Once added, OmniRoute will instantly route all queries through your high-speed free connection with 0 rate limit issues!\n\n"
                                "*Tip: You can also set `GEMINI_API_KEY` directly in your JARVIS settings or `.env` file for direct instant fallback.*"
                            ),
                            tool_calls=[]
                        )
                    return AIResponse(
                        content=f"OmniRoute Gateway error ({res.status_code}): {res.text}",
                        tool_calls=[]
                    )
                raw_text = res.text.strip()

            content = ""
            tool_calls = []
            tokens = 0

            # Case 1: Standard JSON response
            if raw_text.startswith("{") and raw_text.endswith("}"):
                try:
                    data = json.loads(raw_text)
                    choice = data.get("choices", [{}])[0].get("message", {})
                    content = choice.get("content") or ""
                    tokens = data.get("usage", {}).get("total_tokens", 0)

                    if "tool_calls" in choice and choice["tool_calls"]:
                        for tc in choice["tool_calls"]:
                            try:
                                args = json.loads(tc["function"]["arguments"]) if isinstance(tc["function"]["arguments"], str) else tc["function"]["arguments"]
                            except Exception:
                                args = {}
                            tool_calls.append(ToolCallRequest(
                                id=tc.get("id", "call"),
                                name=tc["function"]["name"],
                                arguments=args
                            ))
                    return AIResponse(content=content, tool_calls=tool_calls, tokens_used=tokens, raw_response=data)
                except Exception:
                    pass

            # Case 2: SSE Stream chunks (data: {...})
            content_parts = []
            for line in raw_text.splitlines():
                line = line.strip()
                if line.startswith("data:"):
                    chunk_str = line[5:].strip()
                    if chunk_str == "[DONE]":
                        continue
                    try:
                        chunk_json = json.loads(chunk_str)
                        choices = chunk_json.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                content_parts.append(delta["content"])
                    except Exception:
                        continue

            final_text = "".join(content_parts) or raw_text
            return AIResponse(
                content=final_text,
                tool_calls=tool_calls,
                tokens_used=len(final_text.split())
            )

        except httpx.ConnectError:
            msg = (
                "⚠️ OmniRoute Gateway is not running locally on " + self.base_url + ".\n\n"
                "To start OmniRoute with ~1.51B free tokens, run:\n"
                "```powershell\nomniroute\n```\n"
            )
            logger.warning(msg)
            return AIResponse(content=msg, tool_calls=[])
        except Exception as e:
            logger.error(f"OmniRoute connection exception: {str(e)}")
            return AIResponse(content=f"OmniRoute Connection Error: {str(e)}", tool_calls=[])
