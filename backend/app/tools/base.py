from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from backend.app.security.permissions import PermissionLevel

class ToolResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

class BaseTool(ABC):
    name: str
    description: str
    category: str = "General"
    permission_level: PermissionLevel = PermissionLevel.SAFE
    parameters: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "permission_level": self.permission_level.value,
            "parameters": self.parameters
        }
