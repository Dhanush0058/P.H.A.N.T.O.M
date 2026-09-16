from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from backend.app.memory.manager import memory_manager

router = APIRouter(prefix="/api/memory", tags=["Memory"])

class CreateMemoryRequest(BaseModel):
    key: str
    value: str
    type: str = "fact"

@router.get("")
async def list_memories(query: Optional[str] = ""):
    return await memory_manager.long_term.search(query or "")

@router.post("")
async def create_memory(req: CreateMemoryRequest):
    return await memory_manager.long_term.remember(req.key, req.value, memory_type=req.type)

@router.delete("/{key}")
async def delete_memory(key: str):
    deleted = await memory_manager.long_term.forget(key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory key not found")
    return {"success": True, "key": key}
