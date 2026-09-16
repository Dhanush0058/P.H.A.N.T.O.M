from typing import Optional
from fastapi import APIRouter, UploadFile, File, Response, HTTPException
from pydantic import BaseModel
from backend.app.voice.tts import tts_provider
from backend.app.voice.stt import stt_provider, wake_word_detector
from backend.app.agent.agent import jarvis_agent

router = APIRouter(prefix="/api/voice", tags=["Voice"])

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None

class WakeWordCheckRequest(BaseModel):
    transcript: str

@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    if req.voice:
        tts_provider.voice = req.voice
    audio_bytes = await tts_provider.synthesize(req.text)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Failed to synthesize audio")
    return Response(content=audio_bytes, media_type="audio/mpeg")

@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    audio_data = await file.read()
    transcript = await stt_provider.transcribe(audio_data, mime_type=file.content_type or "audio/webm")
    return {"transcript": transcript}

@router.post("/check-wakeword")
async def check_wakeword(req: WakeWordCheckRequest):
    detected = wake_word_detector.check_phrase(req.transcript)
    return {"detected": detected, "phrase": req.transcript}
