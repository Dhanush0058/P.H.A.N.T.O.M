from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
import asyncio

class PermissionLevel(str, Enum):
    SAFE = "SAFE"            # Automatically executed without prompting
    CONFIRM = "CONFIRM"      # User confirmation required
    DANGEROUS = "DANGEROUS"# High-risk action, dual explicit confirmation
    BLOCKED = "BLOCKED"      # Explicitly prohibited

class PermissionRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str
    action_summary: str
    permission_level: PermissionLevel
    parameters: Dict[str, Any]
    details: Optional[str] = None
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED

class PermissionManager:
    def __init__(self):
        self._pending_requests: Dict[str, PermissionRequest] = {}
        self._futures: Dict[str, asyncio.Future] = {}

    def create_request(self, tool_name: str, action_summary: str, permission_level: PermissionLevel, parameters: Dict[str, Any], details: Optional[str] = None) -> PermissionRequest:
        req = PermissionRequest(
            tool_name=tool_name,
            action_summary=action_summary,
            permission_level=permission_level,
            parameters=parameters,
            details=details
        )
        self._pending_requests[req.id] = req
        try:
            loop = asyncio.get_running_loop()
            self._futures[req.id] = loop.create_future()
        except RuntimeError:
            # When outside an active async event loop (e.g. sync test), future will be bound in wait_for_approval
            pass
        return req

    async def wait_for_approval(self, request_id: str, timeout_seconds: float = 120.0) -> bool:
        if request_id not in self._futures:
            loop = asyncio.get_running_loop()
            self._futures[request_id] = loop.create_future()
        future = self._futures.get(request_id)
        if not future:
            return False
        try:
            result = await asyncio.wait_for(future, timeout=timeout_seconds)
            return result
        except asyncio.TimeoutError:
            self.resolve_request(request_id, approved=False)
            return False
        finally:
            self._futures.pop(request_id, None)
            self._pending_requests.pop(request_id, None)

    def resolve_request(self, request_id: str, approved: bool) -> bool:
        req = self._pending_requests.get(request_id)
        if req:
            req.status = "APPROVED" if approved else "REJECTED"
        fut = self._futures.get(request_id)
        if fut and not fut.done():
            fut.set_result(approved)
            return True
        return req is not None

    def list_pending(self) -> List[PermissionRequest]:
        return list(self._pending_requests.values())

permission_manager = PermissionManager()
