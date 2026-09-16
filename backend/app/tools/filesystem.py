import os
import shutil
from pathlib import Path
from typing import Optional, List
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.security.sandbox import path_sandbox
from backend.app.core.logging import logger

class ListFilesTool(BaseTool):
    name = "list_files"
    description = "Lists files and subdirectories within a target path."
    category = "Filesystem"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Path to inspect (defaults to project workspace root if empty)"
            }
        }
    }

    async def execute(self, directory_path: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            target = path_sandbox.sanitize_path(directory_path or ".")
            if not target.exists() or not target.is_dir():
                return ToolResult(success=False, error=f"Directory '{target}' does not exist.")

            items = []
            for entry in target.iterdir():
                items.append({
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size_bytes": entry.stat().st_size if entry.is_file() else None
                })
            return ToolResult(success=True, data={"directory": str(target), "items": items[:100]}, message=f"Found {len(items)} items in {target.name or str(target)}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads content from a text file (code, markdown, json, txt)."
    category = "Filesystem"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path of the file to read"},
            "max_lines": {"type": "integer", "description": "Maximum lines to read (default 200)"}
        },
        "required": ["file_path"]
    }

    async def execute(self, file_path: str, max_lines: int = 200, **kwargs) -> ToolResult:
        try:
            target = path_sandbox.sanitize_path(file_path)
            if not path_sandbox.is_safe_read_path(target):
                return ToolResult(success=False, error="Access to sensitive system file blocked.")
            if not target.exists() or not target.is_file():
                return ToolResult(success=False, error=f"File '{target}' not found.")

            with open(target, "r", encoding="utf-8", errors="replace") as f:
                lines = [f.readline() for _ in range(max_lines)]
                content = "".join(lines)
            return ToolResult(success=True, data={"file_path": str(target), "content": content}, message=f"Read {len(lines)} lines from {target.name}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Writes or overwrites text content to a specified file."
    category = "Filesystem"
    permission_level = PermissionLevel.CONFIRM
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path of the file to write to"},
            "content": {"type": "string", "description": "Text content to write"}
        },
        "required": ["file_path", "content"]
    }

    async def execute(self, file_path: str, content: str, **kwargs) -> ToolResult:
        try:
            target = path_sandbox.sanitize_path(file_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(success=True, data={"file_path": str(target), "bytes_written": len(content.encode("utf-8"))}, message=f"Successfully wrote to {target.name}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Permanently deletes a file or directory. High risk."
    category = "Filesystem"
    permission_level = PermissionLevel.DANGEROUS
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to delete"}
        },
        "required": ["file_path"]
    }

    async def execute(self, file_path: str, **kwargs) -> ToolResult:
        try:
            target = path_sandbox.sanitize_path(file_path)
            if not target.exists():
                return ToolResult(success=False, error=f"Path '{target}' does not exist.")
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            return ToolResult(success=True, data={"deleted_path": str(target)}, message=f"Permanently deleted {target.name}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
