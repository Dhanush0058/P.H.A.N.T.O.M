from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict
from backend.app.core.config import settings
from backend.app.agent.agent import jarvis_agent, create_ai_provider

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class SettingsUpdateRequest(BaseModel):
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    omniroute_base_url: Optional[str] = None
    omniroute_model: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    custom_llm_api_url: Optional[str] = None
    tts_voice: Optional[str] = None
    wake_word: Optional[str] = None
    app_aliases: Optional[Dict[str, str]] = None

@router.get("")
async def get_current_settings():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL,
        "omniroute_base_url": settings.OMNIROUTE_BASE_URL,
        "omniroute_model": settings.OMNIROUTE_MODEL,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_anthropic_key": bool(settings.ANTHROPIC_API_KEY),
        "custom_llm_api_url": settings.CUSTOM_LLM_API_URL,
        "tts_voice": settings.DEFAULT_TTS_VOICE,
        "wake_word": settings.WAKE_WORD,
        "app_aliases": settings.APP_ALIASES
    }

@router.post("")
async def update_settings(req: SettingsUpdateRequest):
    if req.ai_provider:
        settings.AI_PROVIDER = req.ai_provider
    if req.ai_model:
        settings.AI_MODEL = req.ai_model
    if req.omniroute_base_url is not None:
        settings.OMNIROUTE_BASE_URL = req.omniroute_base_url
    if req.omniroute_model is not None:
        settings.OMNIROUTE_MODEL = req.omniroute_model
    if req.ollama_base_url is not None:
        settings.OLLAMA_BASE_URL = req.ollama_base_url
    if req.ollama_model is not None:
        settings.OLLAMA_MODEL = req.ollama_model
    if req.gemini_api_key is not None:
        settings.GEMINI_API_KEY = req.gemini_api_key
    if req.openai_api_key is not None:
        settings.OPENAI_API_KEY = req.openai_api_key
    if req.anthropic_api_key is not None:
        settings.ANTHROPIC_API_KEY = req.anthropic_api_key
    if req.custom_llm_api_url is not None:
        settings.CUSTOM_LLM_API_URL = req.custom_llm_api_url
    if req.tts_voice:
        settings.DEFAULT_TTS_VOICE = req.tts_voice
    if req.wake_word:
        settings.WAKE_WORD = req.wake_word
    if req.app_aliases:
        settings.APP_ALIASES.update(req.app_aliases)

    # Re-instantiate agent provider
    new_prov = create_ai_provider(settings.AI_PROVIDER)
    jarvis_agent.set_ai_provider(new_prov)

    return {"success": True, "message": "Settings updated successfully"}
