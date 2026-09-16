import pytest
from pathlib import Path
from backend.app.tools.registry import tool_registry
from backend.app.tools.filesystem import WriteFileTool, ReadFileTool, DeleteFileTool
from backend.app.tools.system_tools import GetSystemStatusTool
from backend.app.security.permissions import PermissionLevel

@pytest.mark.asyncio
async def test_tool_registry():
    tools = tool_registry.list_tools()
    assert len(tools) >= 10
    assert tool_registry.get_tool("open_application") is not None
    assert tool_registry.get_tool("get_system_status") is not None
    assert tool_registry.get_tool("search_web") is not None

@pytest.mark.asyncio
async def test_system_status_tool():
    tool = GetSystemStatusTool()
    res = await tool.execute()
    assert res.success is True
    assert "cpu" in res.data
    assert "memory" in res.data

@pytest.mark.asyncio
async def test_filesystem_tools(tmp_path):
    test_file = tmp_path / "jarvis_unit_test.txt"
    writer = WriteFileTool()
    reader = ReadFileTool()
    deleter = DeleteFileTool()

    # Write
    w_res = await writer.execute(file_path=str(test_file), content="JARVIS Online Verification")
    assert w_res.success is True

    # Read
    r_res = await reader.execute(file_path=str(test_file))
    assert r_res.success is True
    assert "JARVIS Online Verification" in r_res.data["content"]

    # Delete
    d_res = await deleter.execute(file_path=str(test_file))
    assert d_res.success is True
    assert not test_file.exists()
