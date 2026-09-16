from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.agent.agent import jarvis_agent
from backend.app.database.database import get_db, AsyncSessionLocal
from backend.app.database.models import Conversation, Message
from sqlalchemy import select

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    tools_invoked: List[str]
    plan: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None

@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    cid = req.conversation_id
    if not cid:
        async with AsyncSessionLocal() as session:
            conv = Conversation(title=req.message[:40] if req.message else "Conversation")
            session.add(conv)
            await session.commit()
            await session.refresh(conv)
            cid = conv.id

    result = await jarvis_agent.process_user_request(
        user_text=req.message,
        conversation_id=cid
    )

    return ChatResponse(
        response=result["response"],
        tools_invoked=result["tools_invoked"],
        plan=result.get("plan"),
        conversation_id=cid
    )

@router.get("/conversations")
async def list_conversations():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Conversation).order_by(Conversation.updated_at.desc()))
        convs = res.scalars().all()
        return [{"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()} for c in convs]

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()))
        msgs = res.scalars().all()
        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "tool_calls": m.tool_calls,
                "created_at": m.created_at.isoformat()
            }
            for m in msgs
        ]
