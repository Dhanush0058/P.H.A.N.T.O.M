import pytest
from backend.app.agent.agent import JarvisAgent
from backend.app.ai.mock import MockAIProvider
from backend.app.database.database import init_db

@pytest.mark.asyncio
async def test_agent_reasoning_and_tool_call():
    await init_db()
    mock_provider = MockAIProvider()
    agent = JarvisAgent(ai_provider=mock_provider)

    events_received = []
    async def mock_broadcast(event: str, data: dict):
        events_received.append((event, data))

    # Test status tool invocation via mock
    res = await agent.process_user_request(
        user_text="What is my system status?",
        broadcast_callback=mock_broadcast
    )

    assert res["response"] is not None
    assert "get_system_status" in res["tools_invoked"]
    assert any(e[0] == "assistant.tool_call" for e in events_received)
    assert any(e[0] == "assistant.tool_result" for e in events_received)
