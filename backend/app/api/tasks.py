from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, delete
from backend.app.database.database import AsyncSessionLocal
from backend.app.database.models import Task

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_at: Optional[datetime] = None

class UpdateTaskRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None

@router.get("")
async def list_tasks():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Task).order_by(Task.created_at.desc()))
        tasks = res.scalars().all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "due_at": t.due_at.isoformat() if t.due_at else None
            }
            for t in tasks
        ]

@router.post("")
async def create_task(req: CreateTaskRequest):
    async with AsyncSessionLocal() as session:
        t = Task(
            title=req.title,
            description=req.description,
            priority=req.priority,
            due_at=req.due_at
        )
        session.add(t)
        await session.commit()
        await session.refresh(t)
        return {
            "id": t.id,
            "title": t.title,
            "status": t.status
        }

@router.patch("/{task_id}")
async def update_task(task_id: str, req: UpdateTaskRequest):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Task).where(Task.id == task_id))
        t = res.scalar_one_or_none()
        if not t:
            raise HTTPException(status_code=404, detail="Task not found")
        if req.status:
            t.status = req.status
            if req.status == "completed":
                t.completed_at = datetime.utcnow()
        if req.priority:
            t.priority = req.priority
        await session.commit()
        return {"success": True, "id": task_id, "status": t.status}

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    async with AsyncSessionLocal() as session:
        res = await session.execute(delete(Task).where(Task.id == task_id))
        await session.commit()
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"success": True, "id": task_id}
