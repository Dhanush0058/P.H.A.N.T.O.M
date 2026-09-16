from sqlalchemy import select, delete, update
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.database.database import AsyncSessionLocal
from backend.app.database.models import Memory as DBMemory
from backend.app.core.logging import logger

class LongTermMemory:
    """Manages persistent facts, preferences, and project contexts stored in SQLite."""
    async def remember(self, key: str, value: str, memory_type: str = "fact", source: str = "user_stated") -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            stmt = select(DBMemory).where(DBMemory.key == key)
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if existing:
                existing.value = value
                existing.type = memory_type
                existing.updated_at = datetime.utcnow()
                await session.commit()
                logger.info(f"Updated long-term memory: key='{key}'")
                return {"id": existing.id, "key": key, "value": value, "status": "updated"}
            else:
                new_mem = DBMemory(key=key, value=value, type=memory_type, source=source)
                session.add(new_mem)
                await session.commit()
                await session.refresh(new_mem)
                logger.info(f"Created new long-term memory: key='{key}'")
                return {"id": new_mem.id, "key": key, "value": value, "status": "created"}

    async def recall(self, key: str) -> Optional[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            stmt = select(DBMemory).where(DBMemory.key == key)
            res = await session.execute(stmt)
            mem = res.scalar_one_or_none()
            if mem:
                return {"id": mem.id, "key": mem.key, "value": mem.value, "type": mem.type}
            return None

    async def forget(self, key: str) -> bool:
        async with AsyncSessionLocal() as session:
            stmt = delete(DBMemory).where(DBMemory.key == key)
            res = await session.execute(stmt)
            await session.commit()
            deleted = res.rowcount > 0
            if deleted:
                logger.info(f"Deleted long-term memory: key='{key}'")
            return deleted

    async def search(self, query: str = "", memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            stmt = select(DBMemory)
            if query:
                stmt = stmt.where((DBMemory.key.ilike(f"%{query}%")) | (DBMemory.value.ilike(f"%{query}%")))
            if memory_type:
                stmt = stmt.where(DBMemory.type == memory_type)
            res = await session.execute(stmt)
            items = res.scalars().all()
            return [
                {
                    "id": m.id,
                    "key": m.key,
                    "value": m.value,
                    "type": m.type,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                }
                for m in items
            ]
