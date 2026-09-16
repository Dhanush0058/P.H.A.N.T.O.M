import json
import re
import httpx
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage, AIResponse, ToolCallRequest
from backend.app.core.config import settings
from backend.app.core.logging import logger

TOOL_SYSTEM_INSTRUCTION = """
You have access to these specific tools:
{tool_descriptions}

CRITICAL RULES:
1. For normal conversations, chatting, answering questions, greetings, or persona changes: RESPOND DIRECTLY IN PLAIN NATURAL LANGUAGE. DO NOT OUTPUT JSON.
2. If the user's input is incomplete, ambiguous, or just a greeting (e.g. "Jarvis", "Jarvis message", "Hello", "Help"), DO NOT call tools. Respond in natural language asking who/what they need.
3. NEVER assume recipients or message bodies for communication tools like `send_whatsapp_message`.
4. ONLY when the user explicitly gives a complete command to interact with files, run terminal commands, or launch a specific program, output a JSON block in this exact format:
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
5. NEVER call `open_application` unless the user explicitly requested to open an app (e.g. "open Chrome", "launch VS Code").
6. If a tool has already been executed in the conversation above, DO NOT repeat the tool call. Reply with a natural confirmation in plain text.
"""

class OllamaProvider(AIProvider):
    """
    Dedicated Local LLM Provider using Ollama (100% Free, Infinite Tokens, Zero Rate Limits, Runs Offline).
    Supports models like qwen2.5-coder:7b, llama3.2, mistral, deepseek-r1, etc.
    """
    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        super().__init__(model_name or settings.OLLAMA_MODEL or settings.AI_MODEL or "qwen2.5-coder:7b")
        # Default Ollama native base is http://localhost:11434
        raw_url = (base_url or settings.OLLAMA_BASE_URL or "http://localhost:11434").rstrip("/")
        if not raw_url.endswith("/v1"):
            self.api_base = f"{raw_url}/v1"
            self.ollama_root = raw_url
        else:
            self.api_base = raw_url
            self.ollama_root = raw_url[:-3]

    async def check_health(self) -> Dict[str, Any]:
        """Check if local Ollama is running and get list of installed models."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.ollama_root}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return {
                        "online": True,
                        "models": models,
                        "current_model": self.model_name,
                        "base_url": self.ollama_root
                    }
        except Exception as e:
            return {"online": False, "error": str(e), "base_url": self.ollama_root}
        return {"online": False, "base_url": self.ollama_root}

    async def generate(self, messages: List[AIMessage], system_prompt: Optional[str] = None) -> AIResponse:
        return await self.generate_with_tools(messages, tools=[], system_prompt=system_prompt)

    async def generate_with_tools(
        self,
        messages: List[AIMessage],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        # Check installed models or adjust fallback instruction
        tools_desc = []
        if tools:
            for t in tools:
                tools_desc.append(f"- {t.get('name')}: {t.get('description')}. Parameters: {json.dumps(t.get('parameters', {}))}")
            tools_text = "\n".join(tools_desc)
            augmented_system = (system_prompt or "") + "\n\n" + TOOL_SYSTEM_INSTRUCTION.format(tool_descriptions=tools_text)
        else:
            augmented_system = system_prompt

        formatted_messages = []
        if augmented_system:
            formatted_messages.append({"role": "system", "content": augmented_system})

        # Keep only the last 6 recent turns to prevent cross-turn hallucination and speed up local inference
        recent_messages = messages[-6:] if len(messages) > 6 else messages
        for m in recent_messages:
            formatted_messages.append({"role": m.role, "content": m.content or ""})

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": 0.2,
            "stream": False,
            "options": {
                "num_ctx": 2048,
                "num_predict": 512
            }
        }

        # Ollama v0.3+ supports OpenAI tools format
        if tools:
            payload["tools"] = tools

        try:
            timeout_cfg = httpx.Timeout(60.0, connect=3.0)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                res = await client.post(f"{self.api_base}/chat/completions", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choice = data.get("choices", [{}])[0].get("message", {})
                    content = choice.get("content") or ""
                    tool_calls: List[ToolCallRequest] = []

                    # 1. Native Ollama function call parsing
                    if "tool_calls" in choice and choice["tool_calls"]:
                        for tc in choice["tool_calls"]:
                            fn = tc.get("function", {})
                            args = fn.get("arguments", {})
                            if isinstance(args, str):
                                try:
                                    args = json.loads(args)
                                except Exception:
                                    args = {}
                            tool_calls.append(ToolCallRequest(
                                id=tc.get("id", f"call_{fn.get('name')}"),
                                name=fn.get("name", "unknown_tool"),
                                arguments=args
                            ))

                    # 2. Prompt-based JSON fallback extraction
                    if not tool_calls and content:
                        parsed_calls = self._extract_tool_calls_from_text(content)
                        if parsed_calls:
                            tool_calls.extend(parsed_calls)

                    # 3. Clean up hallucinated conversational JSON (e.g. {"name": "say_hello", "arguments": {"message": "..."}})
                    if not tool_calls and content:
                        content = self._sanitize_conversational_json(content)

                    return AIResponse(
                        content=content,
                        tool_calls=tool_calls,
                        tokens_used=data.get("usage", {}).get("total_tokens", len(content.split())),
                        raw_response=data
                    )
                else:
                    err_msg = res.text
                    if res.status_code == 404 and "model" in err_msg:
                        return AIResponse(
                            content=(
                                f"⚠️ **Model `{self.model_name}` not found in Ollama.**\n\n"
                                f"To pull and run this model, execute in your terminal:\n"
                                f"```powershell\nollama run {self.model_name}\n```"
                            ),
                            tool_calls=[]
                        )
                    return AIResponse(
                        content=f"Ollama returned status {res.status_code}: {err_msg}",
                        tool_calls=[]
                    )

        except httpx.ConnectError:
            msg = (
                "⚠️ **Local Ollama is not running on `http://localhost:11434`**\n\n"
                "To start Ollama for **100% free, unlimited, offline AI**:\n"
                "1. Download and install Ollama from [ollama.com](https://ollama.com)\n"
                "2. Open a terminal and run your desired model, for example:\n"
                "   ```powershell\n"
                "   ollama run qwen2.5-coder:7b\n"
                "   # or for lightweight laptops:\n"
                "   ollama run llama3.2:3b\n"
                "   ```\n"
                "3. Once running, JARVIS will automatically connect with zero limits!"
            )
            logger.warning("Ollama connection failed: server not listening on localhost:11434")
            return AIResponse(content=msg, tool_calls=[])
        except Exception as e:
            logger.error(f"Ollama error: {str(e)}")
            return AIResponse(content=f"Ollama Error: {str(e)}", tool_calls=[])

    def _sanitize_conversational_json(self, text: str) -> str:
        """
        Unwrap conversational JSON structures like:
        { "name": "say_hello", "arguments": { "message": "Hello!" } }
        into clean spoken text "Hello!".
        """
        stripped = text.strip()
        # Case A: ```json { ... } ```
        code_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', stripped, re.DOTALL)
        if code_match:
            try:
                data = json.loads(code_match.group(1))
                return self._extract_text_from_json_dict(data) or stripped
            except Exception:
                pass

        # Case B: Raw JSON object {...}
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                data = json.loads(stripped)
                extracted = self._extract_text_from_json_dict(data)
                if extracted:
                    return extracted
            except Exception:
                pass

        return text

    def _extract_text_from_json_dict(self, data: Dict[str, Any]) -> Optional[str]:
        # Check arguments/parameters
        args = data.get("arguments") or data.get("parameters") or {}
        if isinstance(args, dict):
            for key in ["message", "text", "response", "content", "msg", "say"]:
                if key in args and isinstance(args[key], str):
                    return args[key]

        for key in ["message", "text", "response", "content", "output"]:
            if key in data and isinstance(data[key], str):
                return data[key]

        return None

    def _extract_tool_calls_from_text(self, text: str) -> List[ToolCallRequest]:
        calls = []
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
