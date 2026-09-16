from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from backend.app.ai.base import AIProvider, AIMessage

class TaskStep(BaseModel):
    step_id: int
    action: str
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, in_progress, completed, failed

class ExecutionPlan(BaseModel):
    goal: str
    steps: List[TaskStep] = Field(default_factory=list)
    estimated_difficulty: str = "simple"  # simple, multi-step, complex

class TaskPlanner:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    async def plan(self, user_goal: str) -> ExecutionPlan:
        # Check if the goal is a multi-step task
        is_multi_step = any(w in user_goal.lower() for w in [" and ", " then ", "after that", "search and", "summarize and", "inspect and"])
        if not is_multi_step:
            return ExecutionPlan(
                goal=user_goal,
                steps=[TaskStep(step_id=1, action=user_goal)],
                estimated_difficulty="simple"
            )

        prompt = f"""Decompose this user goal into 2-5 clear sequential steps:
Goal: "{user_goal}"
Return each step on a new line prefixed with Step N: <action>"""

        resp = await self.ai_provider.generate([AIMessage(role="user", content=prompt)])
        lines = resp.content.split("\n")
        steps = []
        idx = 1
        for line in lines:
            line = line.strip()
            if line and ("step" in line.lower() or line[0].isdigit()):
                clean_action = line.lstrip("0123456789.- :Step")
                steps.append(TaskStep(step_id=idx, action=clean_action))
                idx += 1

        if not steps:
            steps = [TaskStep(step_id=1, action=user_goal)]

        return ExecutionPlan(goal=user_goal, steps=steps, estimated_difficulty="multi-step")
