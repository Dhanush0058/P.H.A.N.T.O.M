import pytest
from backend.app.agent.agent import JarvisAgent
from backend.app.ai.mock import MockAIProvider
from backend.app.database.database import init_db
from backend.app.memory.manager import memory_manager

@pytest.mark.asyncio
async def test_whatsapp_intent_and_contact_memory():
    await init_db()
    mock_provider = MockAIProvider()
    agent = JarvisAgent(ai_provider=mock_provider)

    events = []
    async def mock_broadcast(event: str, data: dict):
        events.append((event, data))

    # 1. Save contact
    res1 = await agent.process_user_request(
        user_text="remember Govardhan's number is +919347249697",
        broadcast_callback=mock_broadcast
    )
    assert "+919347249697" in res1["response"]

    # 2. Recall contact directly
    phone = await memory_manager.get_user_profile_value("govardhan")
    assert phone == "+919347249697"

    # 3. Clear chat
    res_clear = await agent.process_user_request(
        user_text="clear chat",
        broadcast_callback=mock_broadcast
    )
    assert "cleared" in res_clear["response"].lower()
    assert len(memory_manager.short_term.get_messages()) == 0
