import os
import io
import httpx
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger

class SpeechToTextProvider:
    """
    STT Provider supporting WebSpeech API direct stream from frontend,
    with server-side fallback endpoints.
    """
    def __init__(self):
        pass

    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        # If OpenAI key is available, can use Whisper API
        if settings.OPENAI_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
                files = {"file": ("audio.webm", audio_bytes, mime_type)}
                data = {"model": "whisper-1"}
                async with httpx.AsyncClient(timeout=30.0) as client:
                    res = await client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data)
                    if res.status_code == 200:
                        return res.json().get("text", "")
            except Exception as e:
                logger.error(f"Whisper STT error: {str(e)}")
        return ""

class WakeWordDetector:
    """
    Wake word detector monitoring for 'Hey Jarvis' triggers.
    """
    def __init__(self, wake_word: Optional[str] = None):
        self.wake_word = (wake_word or settings.WAKE_WORD).lower()

    def check_phrase(self, text: str) -> bool:
        clean = text.lower().strip()
        return self.wake_word in clean or "jarvis" in clean

stt_provider = SpeechToTextProvider()
wake_word_detector = WakeWordDetector()
