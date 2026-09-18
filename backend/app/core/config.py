from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, Dict
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BASE_DIR.parent
DATA_DIR = WORKSPACE_DIR / "data"
LOGS_DIR = WORKSPACE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Always use canonical absolute SQLite URI (e.g., sqlite+aiosqlite:///C:/.../data/jarvis.db)
CANONICAL_DB_FILE = (DATA_DIR / "jarvis.db").resolve().as_posix()
CANONICAL_DB_URL = f"sqlite+aiosqlite:///{CANONICAL_DB_FILE}"

class Settings(BaseSettings):
    APP_NAME: str = "JARVIS - Personal AI Operating Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    JARVIS_PORT: int = 8000
    PORT: int = 8000

    # AI Configuration (omniroute, mistral, ollama, gemini, openai, anthropic, custom, mock)
    AI_PROVIDER: str = "mistral"
    AI_MODEL: str = "codestral-latest"

    # Mistral AI Cloud (State-of-the-Art Speed, Zero Local RAM)
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "codestral-latest"
    MISTRAL_BASE_URL: str = "https://api.mistral.ai/v1"

    # OmniRoute (1.51B Free Tokens AI Gateway)
    OMNIROUTE_BASE_URL: str = "http://localhost:20128/v1"
    OMNIROUTE_MODEL: str = "auto"
    OMNIROUTE_API_KEY: Optional[str] = "omniroute-free-key"

    # Ollama Local LLM (Infinite Free Tokens, Offline, Zero Rate Limits)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"

    # Standard API Keys (fallback / direct use)
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    CUSTOM_LLM_API_URL: Optional[str] = None
    CUSTOM_LLM_API_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str = CANONICAL_DB_URL

    # Voice / Audio
    DEFAULT_TTS_VOICE: str = "en-US-ChristopherNeural"
    TTS_RATE: str = "+0%"
    WAKE_WORD: str = "hey jarvis"
    VOICE_ENABLED: bool = True

    # Security Guardrails
    AUTO_APPROVE_SAFE: bool = True
    ALLOW_TERMINAL: bool = True
    WORKSPACE_ROOT: str = str(WORKSPACE_DIR)

    # Windows Application Aliases (configurable)
    APP_ALIASES: Dict[str, str] = {
        "vscode": "code",
        "vs code": "code",
        "chrome": "chrome",
        "google chrome": "chrome",
        "notepad": "notepad",
        "terminal": "wt",
        "cmd": "cmd",
        "powershell": "powershell",
        "explorer": "explorer",
        "file explorer": "explorer",
        "calculator": "calc",
        "spotify": "spotify:",
        "whatsapp": "whatsapp:",
        "whatsapp desktop": "whatsapp:",
        "edge": "msedge",
        "microsoft edge": "msedge",
        "browser": "chrome",
        "settings": "ms-settings:",
        "discord": "discord:",
        "telegram": "telegram:",
        "paint": "mspaint"
    }

    # Automatically load .env from project root or current directory
    model_config = SettingsConfigDict(
        env_file=(str(WORKSPACE_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
