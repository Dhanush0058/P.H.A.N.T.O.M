import pytest
import pytest_asyncio
from backend.app.ai.ollama_provider import OllamaProvider
from backend.app.ai.base import AIMessage

@pytest.mark.asyncio
async def test_ollama_provider_init():
    prov = OllamaProvider(model_name="qwen2.5-coder:7b", base_url="http://localhost:11434")
    assert prov.model_name == "qwen2.5-coder:7b"
    assert prov.api_base == "http://localhost:11434/v1"
    assert prov.ollama_root == "http://localhost:11434"

@pytest.mark.asyncio
async def test_ollama_tool_call_extraction():
    prov = OllamaProvider()
    sample_text = """I will list the directory contents for you.
```json
{
  "tool_call": {
    "name": "list_directory",
    "arguments": {
      "path": "."
    }
  }
}
```"""
    calls = prov._extract_tool_calls_from_text(sample_text)
    assert len(calls) == 1
    assert calls[0].name == "list_directory"
    assert calls[0].arguments == {"path": "."}

@pytest.mark.asyncio
async def test_ollama_offline_connection_graceful():
    # Calling non-existent local port should gracefully return helpful message, not throw unhandled exception
    prov = OllamaProvider(base_url="http://127.0.0.1:59999")
    resp = await prov.generate([AIMessage(role="user", content="hello")])
    assert resp is not None
    assert "Ollama" in resp.content or "Error" in resp.content

def test_ollama_conversational_json_sanitizer():
    prov = OllamaProvider()
    raw_json = '{\n  "name": "say_hello",\n  "arguments": {\n    "message": "Hello! How can I assist you today?"\n  }\n}'
    clean = prov._sanitize_conversational_json(raw_json)
    assert clean == "Hello! How can I assist you today?"
