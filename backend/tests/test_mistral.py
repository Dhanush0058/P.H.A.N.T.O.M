import pytest
from backend.app.ai.mistral_provider import MistralProvider
from backend.app.ai.base import AIMessage

@pytest.mark.asyncio
async def test_mistral_provider_init():
    provider = MistralProvider(api_key="test_key", model_name="mistral-small-latest")
    assert provider.model_name == "mistral-small-latest"
    assert provider.api_key == "test_key"
    assert provider.base_url == "https://api.mistral.ai/v1"

@pytest.mark.asyncio
async def test_mistral_missing_key_guidance():
    provider = MistralProvider(api_key="")
    messages = [AIMessage(role="user", content="Hello JARVIS")]
    res = await provider.generate(messages)
    assert "Mistral API Key is missing" in res.content
    assert "console.mistral.ai" in res.content

@pytest.mark.asyncio
async def test_mistral_tool_schema_formatting():
    from backend.app.tools.registry import tool_registry
    provider = MistralProvider(api_key="mock_key")
    raw_schemas = tool_registry.get_tool_schemas()
    # Check that tool schemas have name and parameters
    assert len(raw_schemas) > 0
    assert any(t.get("name") == "open_application" for t in raw_schemas)

