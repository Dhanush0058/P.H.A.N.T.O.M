import pytest
from backend.app.ai.omniroute import OmniRouteProvider
from backend.app.ai.base import AIMessage

@pytest.mark.asyncio
async def test_omniroute_provider_init_and_health():
    prov = OmniRouteProvider(base_url="http://localhost:20128/v1", model_name="auto")
    assert prov.model_name == "auto"
    assert prov.base_url == "http://localhost:20128/v1"

    # Health check should return dictionary without crashing even if offline
    health = await prov.check_health()
    assert "online" in health
    assert "base_url" in health

@pytest.mark.asyncio
async def test_omniroute_offline_graceful_handling():
    # If OmniRoute is offline, provider gives clear actionable instructions without crashing
    prov = OmniRouteProvider(base_url="http://127.0.0.1:59999/v1", model_name="auto")
    resp = await prov.generate([AIMessage(role="user", content="Hello")])
    assert "OmniRoute" in resp.content
