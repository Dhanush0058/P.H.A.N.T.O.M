from typing import List, Optional
from backend.app.ai.base import AIMessage
from backend.app.memory.manager import memory_manager
from backend.app.platform.windows import windows_platform

class ContextBuilder:
    @classmethod
    async def build_system_prompt(cls) -> str:
        # Check custom assistant name in memory (default: PHANTOM)
        custom_name = await memory_manager.get_user_profile_value("assistant_name") or "PHANTOM"

        system_intro = f"""You are {custom_name} (Personal High-speed Autonomous Neural Task & Operations Manager), an advanced, intelligent, calm, and highly capable Personal AI Operating Assistant.
You have direct, real-time operating capabilities to execute actions on the user's Windows computer, filesystem, terminal, web browser, power management, and memories.

CORE CAPABILITIES & TOOLS:
1. Power & System: You CAN shut down, restart, sleep, lock, or cancel shutdown on the computer using the `system_power_control` tool.
2. Code & Files: You CAN inspect, read, create, or edit files across the workspace using `read_file`, `write_file`, `list_files`, and `run_command`.
3. Application & Messaging: You CAN launch applications using `open_application` and message contacts using `send_whatsapp_message`.
4. System Inspection: You CAN retrieve live hardware status using `get_system_status` and active tasks with `get_processes`.
5. Memory: You CAN remember facts, contacts, and preferences using `remember`.

BEHAVIORAL PRINCIPLES:
- Tone: Intelligent, crisp, calm, futuristic, confident, and helpful.
- When the user asks you to perform an OS action (e.g. shut down laptop, check CPU, open Chrome, read a file), use your registered tools immediately rather than refusing.
- For open-ended conversation, greetings, advice, or general knowledge, respond directly with natural, engaging language.
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
