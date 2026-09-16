from typing import List, Dict, Any, Optional
from backend.app.memory.short_term import ShortTermMemory, WorkingMemory
from backend.app.memory.long_term import LongTermMemory

class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.working = WorkingMemory()
        self.long_term = LongTermMemory()

    async def get_user_profile_value(self, key: str) -> Optional[str]:
        """Looks up a specific user profile/fact value from long-term memory."""
        res = await self.long_term.recall(key)
        if res and "value" in res:
            return res["value"]
        # Fallback search
        matches = await self.long_term.search(key)
        if matches:
            return matches[0]["value"]
        return None

    async def get_relevant_memories_for_prompt(self) -> str:
        """Retrieves top long-term preferences and facts to prime the AI assistant."""
        all_mems = await self.long_term.search()
        if not all_mems:
            return ""
        lines = ["User Preferences & Saved Memories:"]
        for m in all_mems[:15]:
            lines.append(f"- [{m['type']}] {m['key']}: {m['value']}")
        return "\n".join(lines)

memory_manager = MemoryManager()
