from typing import List, Optional
from backend.app.ai.base import AIMessage
from backend.app.memory.manager import memory_manager
from backend.app.platform.windows import windows_platform

JARVIS_SYSTEM_PROMPT = """You are JARVIS, a highly advanced, professional, calm, and intelligent Personal AI Operating Assistant.
You have direct, real-time operating capabilities through integrated tools to interact with the user's computer, filesystem, terminal, web browser, and memories.

CORE PRINCIPLES:
1. Tone: Intelligent, concise, professional, calm, slightly futuristic, and honest. Avoid generic chatter or verbose filler.
2. Tool Execution Truthfulness: NEVER pretend to execute an action or state "I opened Chrome" unless the tool was actually executed and returned success.
3. Multi-Step Execution: When a user gives a multi-step command (e.g. "Search for X, summarize, and write to a file"), plan the steps, invoke the appropriate tools, and synthesize the result.
4. Security & Safety: Obey permission boundaries. Destructive actions (deletion, system changes) will be confirmed with the user automatically.
5. Windows Control: When asked to open apps (e.g., VS Code, Chrome, Terminal), invoke `open_application`.
6. Messaging & Contacts: When the user asks to message someone else (e.g. "Govardhan", "Mom"), pass that contact's name or number as the recipient. The user's personal phone number in memory is ONLY for when the user explicitly asks to message themselves.
7. Vision: When asked about what is on screen or diagnosing a screen error, call `take_screenshot`.
"""

class ContextBuilder:
    @classmethod
    async def build_system_prompt(cls) -> str:
        prompt_parts = [JARVIS_SYSTEM_PROMPT]

        # Add live memory context
        mem_context = await memory_manager.get_relevant_memories_for_prompt()
        if mem_context:
            prompt_parts.append("\n" + mem_context)

        # Add brief hardware context
        try:
            metrics = windows_platform.get_system_metrics()
            prompt_parts.append(
                f"\nLive Host Environment: OS=Windows, CPU={metrics['cpu']['usage_percent']}%, RAM={metrics['memory']['percent']}% used"
            )
        except Exception:
            pass

        return "\n".join(prompt_parts)

context_builder = ContextBuilder()
