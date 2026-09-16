import asyncio
from typing import Set, Optional
from backend.app.core.logging import logger

class EmergencyStopManager:
    _instance: Optional["EmergencyStopManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_stopped = False
            cls._instance._active_tasks: Set[asyncio.Task] = set()
        return cls._instance

    @property
    def is_stopped(self) -> bool:
        return self._is_stopped

    def trigger_stop(self) -> int:
        self._is_stopped = True
        cancelled_count = 0
        logger.warning("🛑 EMERGENCY STOP TRIGGERED! Halting all active assistant tasks.")
        for task in list(self._active_tasks):
            if not task.done():
                task.cancel()
                cancelled_count += 1
        self._active_tasks.clear()
        return cancelled_count

    def reset(self):
        self._is_stopped = False
        logger.info("Emergency Stop flag reset to operational status.")

    def register_task(self, task: asyncio.Task):
        self._active_tasks.add(task)
        task.add_done_callback(lambda t: self._active_tasks.discard(t))

emergency_manager = EmergencyStopManager()
