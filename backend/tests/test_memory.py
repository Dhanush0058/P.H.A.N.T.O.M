import pytest
from backend.app.memory.manager import memory_manager
from backend.app.database.database import init_db

@pytest.mark.asyncio
async def test_memory_lifecycle():
    await init_db()

    # Short term memory
    memory_manager.short_term.clear()
    memory_manager.short_term.add_message("user", "Hello Jarvis")
    memory_manager.short_term.add_message("assistant", "Greetings.")
    assert len(memory_manager.short_term.get_messages()) == 2

    # Long term memory
    rem_res = await memory_manager.long_term.remember("main_project", "SnapClass", memory_type="preference")
    assert rem_res["key"] == "main_project"

    rec_res = await memory_manager.long_term.recall("main_project")
    assert rec_res is not None
    assert rec_res["value"] == "SnapClass"

    search_res = await memory_manager.long_term.search("SnapClass")
    assert len(search_res) >= 1

    del_res = await memory_manager.long_term.forget("main_project")
    assert del_res is True
