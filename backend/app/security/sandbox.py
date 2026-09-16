import os
from pathlib import Path
from typing import Optional
from backend.app.core.config import settings

class PathSandbox:
    @classmethod
    def sanitize_path(cls, user_path: str, base_dir: Optional[str] = None) -> Path:
        base = Path(base_dir or settings.WORKSPACE_ROOT).resolve()
        target = Path(user_path).expanduser()
        if not target.is_absolute():
            target = base / target
        target = target.resolve()
        return target

    @classmethod
    def is_safe_read_path(cls, target_path: Path) -> bool:
        # Prevent access to sensitive Windows system credential files
        str_path = str(target_path).lower()
        forbidden_substrings = [
            r"windows\system32\config\sam",
            r"windows\system32\config\system",
            r".ssh\id_rsa",
            r".ssh\id_ed25519",
            r".aws\credentials"
        ]
        for forb in forbidden_substrings:
            if forb in str_path:
                return False
        return True

path_sandbox = PathSandbox()
