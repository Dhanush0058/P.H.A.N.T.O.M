from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.app.tools.registry import tool_registry
from backend.app.agent.executor import tool_executor
from backend.app.security.permissions import permission_manager

router = APIRouter(prefix="/api/tools", tags=["Tools"])

class ExecuteToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}

class ResolvePermissionRequest(BaseModel):
    request_id: str
    approved: bool

@router.get("")
async def list_tools():
    return tool_registry.get_tool_schemas()

@router.post("/execute")
async def execute_tool(req: ExecuteToolRequest):
    result = await tool_executor.execute_tool(req.tool_name, req.parameters)
    return {
        "success": result.success,
        "data": result.data,
        "error": result.error,
        "message": result.message
    }

@router.get("/permissions/pending")
async def get_pending_permissions():
    return permission_manager.list_pending()

@router.post("/permissions/resolve")
async def resolve_permission(req: ResolvePermissionRequest):
    resolved = permission_manager.resolve_request(req.request_id, req.approved)
    if not resolved:
        raise HTTPException(status_code=404, detail="Permission request not found or already completed.")
    return {"success": True, "request_id": req.request_id, "approved": req.approved}
