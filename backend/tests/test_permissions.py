import pytest
from backend.app.security.permissions import PermissionLevel, permission_manager
from backend.app.security.validator import command_validator

def test_command_validator_classification():
    # Safe commands
    lvl, _ = command_validator.classify_command("python --version")
    assert lvl == PermissionLevel.SAFE

    lvl, _ = command_validator.classify_command("git status")
    assert lvl == PermissionLevel.SAFE

    lvl, _ = command_validator.classify_command("dir")
    assert lvl == PermissionLevel.SAFE

    # Confirm commands
    lvl, _ = command_validator.classify_command("pip install fastapi")
    assert lvl == PermissionLevel.CONFIRM

    lvl, _ = command_validator.classify_command("git push origin main")
    assert lvl == PermissionLevel.CONFIRM

    # Dangerous commands
    lvl, _ = command_validator.classify_command("del /f /q myfile.txt")
    assert lvl == PermissionLevel.DANGEROUS

    lvl, _ = command_validator.classify_command("shutdown /s /t 0")
    assert lvl == PermissionLevel.DANGEROUS

    # Blocked commands
    lvl, _ = command_validator.classify_command("mimikatz.exe sekurlsa::logonpasswords")
    assert lvl == PermissionLevel.BLOCKED

    lvl, _ = command_validator.classify_command("format C: /fs:NTFS")
    assert lvl == PermissionLevel.BLOCKED

def test_permission_request_resolution():
    req = permission_manager.create_request(
        tool_name="delete_file",
        action_summary="Delete important file",
        permission_level=PermissionLevel.DANGEROUS,
        parameters={"file_path": "test.txt"}
    )
    assert req.id in [r.id for r in permission_manager.list_pending()]

    resolved = permission_manager.resolve_request(req.id, approved=True)
    assert resolved is True
