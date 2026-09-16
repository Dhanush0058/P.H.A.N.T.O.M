import io
import asyncio
import edge_tts
from typing import Optional
from backend.app.core.config import settings, DATA_DIR
from backend.app.core.logging import logger

class TextToSpeechProvider:
    def __init__(self, voice: Optional[str] = None, rate: Optional[str] = None):
        self.voice = voice or settings.DEFAULT_TTS_VOICE
        self.rate = rate or settings.TTS_RATE

    async def synthesize(self, text: str) -> bytes:
        clean_text = text.strip()
        if not clean_text:
            return b""
        try:
            communicate = edge_tts.Communicate(clean_text, self.voice, rate=self.rate)
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            return audio_buffer.getvalue()
        except Exception as e:
            logger.error(f"TTS Synthesis error: {str(e)}")
            return b""

tts_provider = TextToSpeechProvider()
