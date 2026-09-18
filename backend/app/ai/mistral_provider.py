import json
import httpx
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage, AIResponse, ToolCallRequest
from backend.app.core.config import settings
from backend.app.core.logging import logger

class MistralProvider(AIProvider):
    """
    Mistral AI Cloud Provider (State-of-the-Art Intelligence, Zero Local RAM, Ultra-Fast).
    Supports models like mistral-small-latest, codestral-latest, mistral-large-latest, ministral-8b-latest.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or settings.MISTRAL_API_KEY or ""
        model = model_name or getattr(settings, "MISTRAL_MODEL", "mistral-small-latest")
        if model == "auto":
            model = "mistral-small-latest"
        super().__init__(model)
        self.base_url = (base_url or getattr(settings, "MISTRAL_BASE_URL", "https://api.mistral.ai/v1")).rstrip("/")

    async def check_health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"online": False, "error": "MISTRAL_API_KEY is not configured.", "provider": "mistral"}
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/models", headers=headers)
                if res.status_code == 200:
                    models = [m.get("id") for m in res.json().get("data", [])]
                    return {"online": True, "models": models, "current_model": self.model_name}
                return {"online": False, "status_code": res.status_code, "error": res.text}
        except Exception as e:
            return {"online": False, "error": str(e)}

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
                content=(
                    "⚠️ **Mistral API Key is missing.**\n\n"
                    "To activate Mistral Cloud intelligence with 0% PC load:\n"
                    "1. Get your free API key at **[console.mistral.ai](https://console.mistral.ai)**\n"
                    "2. Open the **JARVIS Settings (⚙️)** on the HUD sidebar.\n"
                    "3. Paste your Mistral API Key and click **Save Changes**."
                ),
                tool_calls=[]
            )

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for m in messages:
            msg_dict: Dict[str, Any] = {"role": m.role, "content": m.content or ""}
            if m.tool_calls:
                formatted_calls = []
                for tc in m.tool_calls:
                    if isinstance(tc, ToolCallRequest):
                        formatted_calls.append({
                            "id": tc.id or f"call_{tc.name}",
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else str(tc.arguments)
                            }
                        })
                if formatted_calls:
                    msg_dict["tool_calls"] = formatted_calls
            if m.tool_call_id:
                msg_dict["tool_call_id"] = m.tool_call_id
            formatted_messages.append(msg_dict)

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": 0.2,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    choice = data.get("choices", [{}])[0].get("message", {})
                    content = choice.get("content") or ""
                    tool_calls: List[ToolCallRequest] = []

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

                    return AIResponse(
                        content=content,
                        tool_calls=tool_calls,
                        tokens_used=data.get("usage", {}).get("total_tokens", 0),
                        raw_response=data
                    )
                elif res.status_code == 401:
                    return AIResponse(
                        content="⚠️ **Invalid Mistral API Key.** Please verify your key at [console.mistral.ai](https://console.mistral.ai) and update it in JARVIS Settings.",
                        tool_calls=[]
                    )
                elif res.status_code == 429:
                    return AIResponse(
                        content="⚠️ **Mistral Rate Limit reached.** Please wait a moment or check your quota on Mistral Console.",
                        tool_calls=[]
                    )
                else:
                    return AIResponse(
                        content=f"Mistral Cloud API Error ({res.status_code}): {res.text}",
                        tool_calls=[]
                    )
        except Exception as e:
            logger.error(f"Mistral Cloud API connection error: {str(e)}")
            return AIResponse(
                content=f"Failed to connect to Mistral Cloud: {str(e)}",
                tool_calls=[]
            )
