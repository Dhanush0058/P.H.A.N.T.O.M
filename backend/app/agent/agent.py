import asyncio
import json
import re
from typing import Optional, Callable, Dict, Any, List
from backend.app.ai.base import AIProvider, AIMessage, AIResponse
from backend.app.ai.omniroute import OmniRouteProvider
from backend.app.ai.mock import MockAIProvider
from backend.app.ai.gemini import GeminiProvider
from backend.app.ai.openai_provider import OpenAIProvider
from backend.app.ai.anthropic_provider import AnthropicProvider
from backend.app.ai.custom_repo import CustomRepoLLMProvider
from backend.app.ai.ollama_provider import OllamaProvider
from backend.app.ai.mistral_provider import MistralProvider
from backend.app.tools.registry import tool_registry
from backend.app.agent.context import context_builder
from backend.app.agent.planner import TaskPlanner
from backend.app.agent.executor import tool_executor
from backend.app.memory.manager import memory_manager
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.database import AsyncSessionLocal
from backend.app.database.models import Conversation, Message as DBMessage

def create_ai_provider(provider_type: Optional[str] = None) -> AIProvider:
    p_type = (provider_type or settings.AI_PROVIDER).lower()
    if p_type == "mistral":
        return MistralProvider()
    elif p_type == "omniroute":
        return OmniRouteProvider()
    elif p_type == "ollama":
        return OllamaProvider(model_name=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL)
    elif p_type == "gemini":
        return GeminiProvider()
    elif p_type == "openai":
        return OpenAIProvider()
    elif p_type == "anthropic":
        return AnthropicProvider()
    elif p_type == "custom":
        return CustomRepoLLMProvider()
    else:
        return MockAIProvider()

class JarvisAgent:
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        self.ai_provider = ai_provider or create_ai_provider()
        self.planner = TaskPlanner(self.ai_provider)

    def set_ai_provider(self, provider: AIProvider):
        self.ai_provider = provider
        self.planner = TaskPlanner(provider)
        logger.info(f"Jarvis AI Provider updated to: {provider.__class__.__name__}")

    async def process_user_request(
        self,
        user_text: str,
        conversation_id: Optional[str] = None,
        broadcast_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Main Agent Reasoning & Execution Loop:
        1. Context Assembly
        2. Plan formulation
        3. Model reasoning with tools
        4. Tool execution & observation loop
        5. Automatic fallback if primary provider fails
        """
        async def broadcast(event: str, data: Dict[str, Any]):
            if broadcast_callback:
                await broadcast_callback(event, data)

        logger.info(f"User Request: '{user_text}'")
        await broadcast("assistant.thinking", {"status": "Analyzing request..."})

        # Save user message to short term memory
        memory_manager.short_term.add_message("user", user_text)

        lower_user = user_text.lower().strip()

        # Handle clear chat / reset
        if lower_user in ["clear chat", "clear history", "reset", "reset chat", "new chat", "new conversation", "clear"]:
            memory_manager.short_term.clear()
            reply = "Conversation context cleared. What can I help you with?"
            await broadcast("assistant.chat_message", {"role": "assistant", "content": reply, "tools_invoked": []})
            await broadcast("assistant.state_change", {"state": "IDLE"})
            return {"response": reply, "tools_invoked": [], "plan": {"goal": user_text, "steps": []}}

        # Handle direct assistant identity/name change
        name_match = re.search(r'(?:change\s+your\s+name\s+to|call\s+yourself|your\s+name\s+is\s+now|name\s+yourself)\s+(?:a\s+|an\s+)?([a-zA-Z0-9_\-]+)', lower_user)
        if name_match:
            new_name = name_match.group(1).capitalize()
            await memory_manager.long_term.remember("assistant_name", new_name, memory_type="preference")
            reply = f"Understood. My name has been changed to {new_name}. How can I assist you today?"
            memory_manager.short_term.add_message("assistant", reply)
            await broadcast("assistant.chat_message", {"role": "assistant", "content": reply, "tools_invoked": []})
            await broadcast("assistant.state_change", {"state": "IDLE"})
            return {"response": reply, "tools_invoked": [], "plan": {"goal": user_text, "steps": []}}

        # Handle contact phone saving (e.g. "remember Govardhan's number is +919347249697")
        contact_save = re.search(r'(?:remember|save\s+contact|save)\s+([a-zA-Z0-9_\-]+)(?:\'s)?\s*(?:phone|number|phone\s+number|contact)?\s*(?:is|as|=|:)?\s*(\+?[0-9\s\-]{7,15})', lower_user)
        if contact_save:
            c_name = contact_save.group(1).strip().lower()
            c_phone = "".join([c for c in contact_save.group(2) if c.isdigit() or c == "+"])
            await memory_manager.long_term.remember(f"contact_{c_name}", c_phone, memory_type="contact")
            await memory_manager.long_term.remember(c_name, c_phone, memory_type="contact")
            reply = f"I've saved {c_name.capitalize()}'s phone number as {c_phone}."
            memory_manager.short_term.add_message("assistant", reply)
            await broadcast("assistant.chat_message", {"role": "assistant", "content": reply, "tools_invoked": []})
            await broadcast("assistant.state_change", {"state": "IDLE"})
            return {"response": reply, "tools_invoked": [], "plan": {"goal": user_text, "steps": []}}

        # Handle contact phone retrieval (e.g. "give me the number of Govardhan from WhatsApp", "what is Govardhan's phone number")
        contact_query1 = re.search(r'(?:give|tell|what\s+is|get|show|find)\s+(?:me\s+)?(?:the\s+)?(?:phone\s+number|phone|number|contact(?:\s+details|\s+info)?)\s+(?:of|for)?\s*([a-zA-Z0-9_\-]+)', lower_user)
        contact_query2 = re.search(r'(?:what\s+is|get|show|find)\s+([a-zA-Z0-9_\-]+)(?:\'s)?\s*(?:phone|number|phone\s+number|contact)', lower_user)
        
        target_contact = None
        if contact_query1:
            target_contact = contact_query1.group(1).strip().lower()
        elif contact_query2:
            target_contact = contact_query2.group(1).strip().lower()

        if target_contact and target_contact not in ["all", "my", "the", "system", "weather"]:
            # Clean filler words like 'from' or 'whatsapp' if caught in the group
            target_contact = re.sub(r'\s+(?:from|in|on)\s+whatsapp.*$', '', target_contact).strip()
            # Look up contact in memory
            found_phone = (
                await memory_manager.get_user_profile_value(target_contact) or
                await memory_manager.get_user_profile_value(f"contact_{target_contact}") or
                await memory_manager.long_term.recall(target_contact) or
                await memory_manager.long_term.recall(f"contact_{target_contact}")
            )
            if isinstance(found_phone, dict) and "value" in found_phone:
                found_phone = found_phone["value"]

            if found_phone:
                reply = f"The phone number for {target_contact.capitalize()} is {found_phone}."
            else:
                reply = f"I do not have a saved phone number for {target_contact.capitalize()} yet. You can say: 'Remember {target_contact.capitalize()}'s number is +91...' to save it."

            memory_manager.short_term.add_message("assistant", reply)
            await broadcast("assistant.chat_message", {"role": "assistant", "content": reply, "tools_invoked": []})
            await broadcast("assistant.state_change", {"state": "IDLE"})
            return {"response": reply, "tools_invoked": [], "plan": {"goal": user_text, "steps": []}}

        # Handle list all contacts (e.g. "list contacts", "show contacts")
        if re.search(r'^(?:list|show|view|get)\s+(?:all\s+)?(?:my\s+)?contacts', lower_user):
            all_mems = await memory_manager.long_term.search(memory_type="contact")
            if not all_mems:
                # Also check general memories
                all_mems = [m for m in (await memory_manager.long_term.search()) if m.get("type") == "contact" or "contact_" in m.get("key", "")]

            if all_mems:
                unique_contacts = {}
                for m in all_mems:
                    k = m["key"].replace("contact_", "").capitalize()
                    unique_contacts[k] = m["value"]
                contact_list = "\n".join([f"• **{k}**: {v}" for k, v in unique_contacts.items()])
                reply = f"Here are your saved contacts:\n\n{contact_list}"
            else:
                reply = "You don't have any contacts saved yet. Say 'Remember <name>'s number is <phone>' to add one."

            memory_manager.short_term.add_message("assistant", reply)
            await broadcast("assistant.chat_message", {"role": "assistant", "content": reply, "tools_invoked": []})
            await broadcast("assistant.state_change", {"state": "IDLE"})
            return {"response": reply, "tools_invoked": [], "plan": {"goal": user_text, "steps": []}}

        # Handle direct WhatsApp automation without hallucination
        wa_match1 = re.search(r'(?:open\s+(?:your\s+)?whatsapp\s+)?search\s+for\s+(?:the\s+)?([a-zA-Z0-9_+]+)\s+and\s+(?:message|text|send\s+message\s+to)\s+(?:him|her|them)?\s*(?:like|as|saying|that|with)?\s*[:"\'\s]*(.*?)$', user_text, re.I)
        wa_match2 = re.search(r'(?:send\s+(?:a\s+)?whatsapp(?:\s+message)?|open\s+(?:your\s+)?whatsapp\s+(?:and\s+)?message|whatsapp\s+message|message\s+on\s+whatsapp)\s+(?:to\s+|for\s+)?([a-zA-Z0-9_+]+)?\s*(?:as|like|saying|that|with|text)?\s*[:"\'\s]*(.*?)$', user_text, re.I)
        
        wa_info = None
        if wa_match1:
            wa_info = {"recipient": wa_match1.group(1).strip(), "message": wa_match1.group(2).strip().strip('"\'') or "Hi"}
        elif wa_match2:
            r = (wa_match2.group(1) or "").strip()
            m = (wa_match2.group(2) or "").strip().strip('"\'') or "Hi"
            if r.lower() not in ["as", "like", "saying", "that", ""]:
                wa_info = {"recipient": r, "message": m}
            else:
                wa_info = {"recipient": "", "message": m}

        if wa_info:
            await broadcast("assistant.state_change", {"state": "EXECUTING"})
            await broadcast("assistant.tool_call", {"tool_id": "call_whatsapp", "name": "send_whatsapp_message", "arguments": wa_info})
            res = await tool_executor.execute_tool("send_whatsapp_message", wa_info, ws_broadcast=broadcast)
            reply = res.message or (f"WhatsApp message sent to {wa_info['recipient']}." if res.success else f"Error: {res.error}")
            memory_manager.short_term.add_message("assistant", reply)
            await broadcast("assistant.chat_message", {"role": "assistant", "content": reply, "tools_invoked": ["send_whatsapp_message"]})
            await broadcast("assistant.state_change", {"state": "IDLE"})
            return {"response": reply, "tools_invoked": ["send_whatsapp_message"], "plan": {"goal": user_text, "steps": []}}

        # Plan task if complex
        plan = await self.planner.plan(user_goal=user_text)
        if len(plan.steps) > 1:
            await broadcast("assistant.plan_update", plan.model_dump())

        # Build prompt & context
        system_prompt = await context_builder.build_system_prompt()
        tool_schemas = tool_registry.get_tool_schemas()

        history = memory_manager.short_term.get_messages()
        current_messages = list(history)

        max_tool_turns = 6
        final_answer = ""
        tools_invoked = []
        executed_signatures = set()
        last_tool_result_msg = ""

        for turn in range(max_tool_turns):
            await broadcast("assistant.thinking", {"status": f"Reasoning (cycle {turn + 1})..."})
            ai_resp: AIResponse = await self.ai_provider.generate_with_tools(
                messages=current_messages,
                tools=tool_schemas,
                system_prompt=system_prompt
            )

            # Check if response returned a 503 retry limit error from OmniRoute
            if "Maximum combo retry limit reached" in ai_resp.content or "status 503" in ai_resp.content:
                logger.warning("OmniRoute public keyless demo limit reached. Attempting fallback.")
                if settings.GEMINI_API_KEY:
                    logger.info("Failing over to configured Gemini provider...")
                    gemini_prov = GeminiProvider()
                    ai_resp = await gemini_prov.generate_with_tools(current_messages, tool_schemas, system_prompt)
                elif settings.OPENAI_API_KEY:
                    logger.info("Failing over to configured OpenAI provider...")
                    openai_prov = OpenAIProvider()
                    ai_resp = await openai_prov.generate_with_tools(current_messages, tool_schemas, system_prompt)
                else:
                    ai_resp.content = (
                        "⚠️ **OmniRoute Notice**: The public demo pool is currently exhausted.\n\n"
                        "To activate permanent, unlimited free routing in OmniRoute:\n"
                        "1. Open **`http://localhost:20128`** in your browser.\n"
                        "2. Click **Connections / Add Provider** and paste any free key (e.g. Groq, Google AI Studio, Mistral, GitHub Models).\n\n"
                        "*Alternatively, configure your `GEMINI_API_KEY` or `OPENAI_API_KEY` in the JARVIS Settings modal (gear icon on the sidebar).*"
                    )

            # Filter out irrelevant or unprompted tool calls
            if ai_resp.tool_calls:
                valid_calls = []
                for tc in ai_resp.tool_calls:
                    if tc.name == "open_application":
                        app_arg = str(tc.arguments.get("app_name", "")).lower()
                        if not any(w in lower_user for w in ["open", "launch", "start", "run", app_arg]) and app_arg != "vscode":
                            logger.info(f"Filtering out irrelevant tool call '{tc.name}' for request '{user_text}'")
                            continue
                        if not any(w in lower_user for w in ["open", "launch", "start", "run", "code", "vscode"]):
                            logger.info(f"Filtering out false positive '{tc.name}' for request '{user_text}'")
                            continue
                    elif tc.name == "send_whatsapp_message":
                        # Require explicit whatsapp context and not just single ambiguous word
                        if not any(w in lower_user for w in ["whatsapp", "text", "send", "msg"]) or len(lower_user.split()) < 3:
                            logger.info(f"Filtering out unprompted/ambiguous '{tc.name}' for request '{user_text}'")
                            continue
                    valid_calls.append(tc)
                ai_resp.tool_calls = valid_calls

                # If the only tool call was filtered out due to ambiguity, ask for clarification
                if not ai_resp.tool_calls and not ai_resp.content:
                    if "message" in lower_user:
                        ai_resp.content = "Who would you like to message on WhatsApp, and what would you like the message to say?"
                    else:
                        ai_resp.content = "I'm here. How can I assist you?"

            # If the model requested tool calls
            if ai_resp.tool_calls:
                # Filter out calls that were already executed with identical arguments
                pending_calls = []
                for tc in ai_resp.tool_calls:
                    sig = f"{tc.name}:{json.dumps(tc.arguments, sort_keys=True)}"
                    if sig in executed_signatures:
                        logger.info(f"Skipping duplicate tool call: {tc.name} with {tc.arguments}")
                        continue
                    executed_signatures.add(sig)
                    pending_calls.append(tc)

                # If all requested calls were duplicates, conclude task immediately
                if not pending_calls:
                    logger.info("All tool calls in this cycle were already executed. Concluding task.")
                    final_answer = last_tool_result_msg or "Task executed successfully."
                    break

                for tc in pending_calls:
                    tools_invoked.append(tc.name)
                    await broadcast("assistant.state_change", {"state": "EXECUTING"})
                    await broadcast("assistant.tool_call", {
                        "tool_id": tc.id,
                        "name": tc.name,
                        "arguments": tc.arguments
                    })

                    # Execute tool via ToolExecutor (handles permissions & timeouts)
                    result = await tool_executor.execute_tool(
                        tool_name=tc.name,
                        parameters=tc.arguments,
                        ws_broadcast=broadcast
                    )

                    await broadcast("assistant.tool_result", {
                        "tool_id": tc.id,
                        "name": tc.name,
                        "success": result.success,
                        "data": result.data,
                        "error": result.error,
                        "message": result.message
                    })

                    last_tool_result_msg = result.message or ("Success" if result.success else f"Error: {result.error}")

                    # Format result back into context
                    res_content = result.message or json.dumps(result.data or {"status": "done", "error": result.error})
                    current_messages.append(AIMessage(
                        role="assistant",
                        content=ai_resp.content,
                        tool_calls=[tc]
                    ))
                    current_messages.append(AIMessage(
                        role="tool",
                        content=f"Tool '{tc.name}' executed with result: {res_content}",
                        tool_call_id=tc.id or tc.name
                    ))

                # Fast-path for direct action tools (no second LLM generation needed)
                info_gathering_tools = {"search_web", "get_page_content", "read_file", "list_files", "git_status", "git_diff", "git_log", "get_system_status", "get_processes", "recall", "search_memory", "take_screenshot"}
                executed_names = {tc.name for tc in pending_calls}
                if not (executed_names & info_gathering_tools):
                    # Direct action completed — finish immediately without redundant 2nd LLM round-trip
                    final_answer = last_tool_result_msg or "Task completed successfully."
                    break

                # Continue loop to allow model to interpret tool result for information gathering
                continue
            else:
                final_answer = ai_resp.content or last_tool_result_msg or "Task completed."
                break

        if not final_answer and not tools_invoked:
            final_answer = "Understood."
        elif not final_answer and last_tool_result_msg:
            final_answer = last_tool_result_msg

        # Add assistant response to short term memory
        memory_manager.short_term.add_message("assistant", final_answer)

        # Store to DB if conversation_id provided
        if conversation_id:
            try:
                async with AsyncSessionLocal() as session:
                    user_db_msg = DBMessage(conversation_id=conversation_id, role="user", content=user_text)
                    jarvis_db_msg = DBMessage(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=final_answer,
                        tool_calls=[{"name": t} for t in tools_invoked] if tools_invoked else None
                    )
                    session.add(user_db_msg)
                    session.add(jarvis_db_msg)
                    await session.commit()
            except Exception as e:
                logger.error(f"Error persisting messages to DB: {str(e)}")

        await broadcast("assistant.chat_message", {
            "role": "assistant",
            "content": final_answer,
            "tools_invoked": tools_invoked
        })
        await broadcast("assistant.state_change", {"state": "IDLE"})

        return {
            "response": final_answer,
            "tools_invoked": tools_invoked,
            "plan": plan.model_dump()
        }

jarvis_agent = JarvisAgent()
