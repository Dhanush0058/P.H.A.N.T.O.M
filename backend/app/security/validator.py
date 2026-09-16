import re
from typing import Tuple
from backend.app.security.permissions import PermissionLevel
from backend.app.core.logging import logger

# Strictly BLOCKED patterns (exploits, password dumping, credential theft, disk wipes)
BLOCKED_PATTERNS = [
    re.compile(r'\b(mimikatz|samdump2|procdump|pwdump|lazagne)\b', re.IGNORECASE),
    re.compile(r'format\s+[a-z]:\s+/fs', re.IGNORECASE),
    re.compile(r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;:\s*', re.IGNORECASE), # Fork bomb
    re.compile(r'(Invoke-Mimikatz|Get-Credential|reg\s+save\s+hklm\\sam)', re.IGNORECASE),
    re.compile(r'rmdir\s+/[sS]\s+/[qQ]\s+c:\\(windows|system32)', re.IGNORECASE),
    re.compile(r'rm\s+-rf\s+/(etc|boot|sys|proc|var)', re.IGNORECASE),
]

# SAFE patterns (benign queries, version checks, directory listing)
SAFE_PATTERNS = [
    re.compile(r'^(python|python3|node|npm|git|cargo|go|rustc)\s+(--version|-v|-V)$', re.IGNORECASE),
    re.compile(r'^(dir|ls|cd|pwd|echo|type|cat|where|which|whoami|hostname|systeminfo|ver)(\s.*)?$', re.IGNORECASE),
    re.compile(r'^git\s+(status|log|diff|branch|show)(\s.*)?$', re.IGNORECASE)
]

# DANGEROUS patterns (require explicit dual confirmation)
DANGEROUS_PATTERNS = [
    re.compile(r'\b(del|rmdir|rm|erase)\s+', re.IGNORECASE),
    re.compile(r'\b(shutdown|reboot|restart-computer)\b', re.IGNORECASE),
    re.compile(r'\b(reg\s+(delete|add)|regedit)\b', re.IGNORECASE),
    re.compile(r'\b(taskkill\s+/f|kill\s+-9|pkill\s+-9)\b', re.IGNORECASE),
    re.compile(r'\b(diskpart|chkdsk\s+/f|cipher\s+/w)\b', re.IGNORECASE),
    re.compile(r'\b(net\s+user|net\s+localgroup)\b', re.IGNORECASE),
    re.compile(r'\b(git\s+reset\s+--hard|git\s+clean\s+-fdx)\b', re.IGNORECASE),
]

# CONFIRM patterns (standard interactive confirmation required)
CONFIRM_PATTERNS = [
    re.compile(r'\b(pip\s+install|npm\s+install|cargo\s+install|go\s+install)\b', re.IGNORECASE),
    re.compile(r'\b(git\s+(push|commit|checkout|branch\s+-D))\b', re.IGNORECASE),
    re.compile(r'\b(python|python3|node|cargo|go|dotnet)\s+[^\s]+', re.IGNORECASE),
    re.compile(r'\b(mkdir|touch|mv|move|ren|rename|cp|copy)\b', re.IGNORECASE),
    re.compile(r'\b(curl|wget|Invoke-WebRequest|Invoke-RestMethod)\b', re.IGNORECASE),
]

class CommandValidator:
    @classmethod
    def classify_command(cls, command: str) -> Tuple[PermissionLevel, str]:
        cmd_clean = command.strip()
        if not cmd_clean:
            return PermissionLevel.SAFE, "Empty command"

        for pat in BLOCKED_PATTERNS:
            if pat.search(cmd_clean):
                logger.warning(f"Security Alert: Blocked forbidden command '{cmd_clean}'")
                return PermissionLevel.BLOCKED, f"Command contains strictly blocked malicious pattern: {pat.pattern}"

        for pat in SAFE_PATTERNS:
            if pat.search(cmd_clean):
                return PermissionLevel.SAFE, "Read-only / benign inspection command."

        for pat in DANGEROUS_PATTERNS:
            if pat.search(cmd_clean):
                return PermissionLevel.DANGEROUS, "Command has destructive or system-altering potential."

        for pat in CONFIRM_PATTERNS:
            if pat.search(cmd_clean):
                return PermissionLevel.CONFIRM, "Command requires confirmation to modify environment or run execution scripts."

        # Default fallback for unknown commands
        return PermissionLevel.CONFIRM, "Arbitrary shell execution requires user approval."

command_validator = CommandValidator()
