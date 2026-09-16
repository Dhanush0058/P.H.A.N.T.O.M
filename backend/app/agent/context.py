from typing import List, Optional
from backend.app.ai.base import AIMessage
from backend.app.memory.manager import memory_manager
from backend.app.platform.windows import windows_platform

class ContextBuilder:
    @classmethod
    async def build_system_prompt(cls) -> str:
        # Check custom assistant name in memory (default: Phantom / JARVIS)
        custom_name = await memory_manager.get_user_profile_value("assistant_name") or "Phantom"

        system_intro = f"""You are {custom_name}, a highly advanced, professional, calm, and intelligent Personal AI Operating Assistant.
You have direct, real-time operating capabilities to interact with the user's computer, filesystem, terminal, web browser, and memories.

CORE PRINCIPLES:
1. Tone: Intelligent, concise, professional, calm, slightly futuristic, and helpful.
2. Conversational vs Tools: For standard conversation, questions, greetings, advice, or identity changes (e.g., "change your name to Phantom"), respond directly in plain natural language.
3. Computer Control: ONLY call `open_application` when the user explicitly requests to open, launch, or start an application. NEVER open random apps like VS Code for conversation or name changes.
4. Messaging & Contacts: When the user asks to message someone else, pass their contact name or number.
5. Multi-Step Execution: Plan and execute multi-step tools when requested.
6. Memory: When asked to remember facts or name preferences, use `remember`.
"""
        prompt_parts = [system_intro]

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
