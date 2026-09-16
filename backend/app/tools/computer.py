import pyautogui
from typing import Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.platform.windows import windows_platform

class OpenApplicationTool(BaseTool):
    name = "open_application"
    description = "Opens a Windows application like VS Code, Chrome, Notepad, Terminal, Explorer, etc."
    category = "Computer"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name or alias of the application (e.g., 'vscode', 'chrome', 'notepad', 'terminal', 'explorer')"
            }
        },
        "required": ["app_name"]
    }

    async def execute(self, app_name: str, **kwargs) -> ToolResult:
        res = windows_platform.open_application(app_name)
        if res.get("success"):
            return ToolResult(success=True, data=res, message=res.get("message"))
        return ToolResult(success=False, error=res.get("error", "Failed to launch application"))

class CloseApplicationTool(BaseTool):
    name = "close_application"
    description = "Closes/terminates running application instances by name."
    category = "Computer"
    permission_level = PermissionLevel.DANGEROUS
    parameters = {
        "type": "object",
        "properties": {
            "process_name": {
                "type": "string",
                "description": "Process name or application to terminate (e.g., 'notepad', 'chrome.exe')"
            }
        },
        "required": ["process_name"]
    }

    async def execute(self, process_name: str, **kwargs) -> ToolResult:
        res = windows_platform.close_application(process_name)
        if res.get("success"):
            return ToolResult(success=True, data=res, message=res.get("message"))
        return ToolResult(success=False, error=res.get("error"))

class TakeScreenshotTool(BaseTool):
    name = "take_screenshot"
    description = "Captures the current screen image and saves it for vision analysis."
    category = "Computer"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {}
    }

    async def execute(self, **kwargs) -> ToolResult:
        res = windows_platform.take_screenshot()
        if res.get("success"):
            return ToolResult(success=True, data=res, message=res.get("message"))
        return ToolResult(success=False, error=res.get("error"))

class MouseControlTool(BaseTool):
    name = "mouse_control"
    description = "Moves mouse cursor or performs clicks at specified screen coordinates."
    category = "Computer"
    permission_level = PermissionLevel.CONFIRM
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["move", "click", "double_click", "right_click"],
                "description": "Mouse action to perform"
            },
            "x": {"type": "integer", "description": "Screen X coordinate"},
            "y": {"type": "integer", "description": "Screen Y coordinate"}
        },
        "required": ["action", "x", "y"]
    }

    async def execute(self, action: str, x: int, y: int, **kwargs) -> ToolResult:
        try:
            if action == "move":
                pyautogui.moveTo(x, y, duration=0.2)
            elif action == "click":
                pyautogui.click(x, y)
            elif action == "double_click":
                pyautogui.doubleClick(x, y)
            elif action == "right_click":
                pyautogui.rightClick(x, y)
            return ToolResult(success=True, data={"action": action, "x": x, "y": y}, message=f"Mouse {action} executed at ({x}, {y})")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class KeyboardControlTool(BaseTool):
    name = "keyboard_control"
    description = "Types text or triggers keyboard hotkeys (e.g., ctrl+s, alt+tab)."
    category = "Computer"
    permission_level = PermissionLevel.CONFIRM
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["type", "hotkey", "press"],
                "description": "Keyboard action"
            },
            "keys": {
                "type": "string",
                "description": "Text to type or hotkey combination separated by comma/plus (e.g., 'ctrl+c', 'enter')"
            }
        },
        "required": ["action", "keys"]
    }

    async def execute(self, action: str, keys: str, **kwargs) -> ToolResult:
        try:
            if action == "type":
                pyautogui.write(keys, interval=0.02)
            elif action == "hotkey":
                parts = [k.strip() for k in keys.replace("+", ",").split(",")]
                pyautogui.hotkey(*parts)
            elif action == "press":
                pyautogui.press(keys.strip())
            return ToolResult(success=True, data={"action": action, "keys": keys}, message=f"Executed keyboard {action}: {keys}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class SendWhatsAppMessageTool(BaseTool):
    name = "send_whatsapp_message"
    description = "Opens WhatsApp and pre-fills or sends a message to a contact/phone number or to self."
    category = "Computer"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message text to send (e.g., 'hi', 'I am on my way')"
            },
            "recipient": {
                "type": "string",
                "description": "Optional phone number with country code (e.g. '+919876543210') or 'myself'"
            }
        },
        "required": ["message"]
    }

    async def execute(self, message: Optional[str] = None, recipient: Optional[str] = None, **kwargs) -> ToolResult:
        import urllib.parse
        import os
        import asyncio
        import subprocess

        actual_message = message or kwargs.get("text") or kwargs.get("msg") or kwargs.get("body") or "Hi"
        encoded_msg = urllib.parse.quote(actual_message)
        clean_recipient = ""
        actual_recipient = recipient or kwargs.get("to") or kwargs.get("phone") or kwargs.get("contact")
        from backend.app.memory.manager import memory_manager

        if actual_recipient:
            rec_clean = actual_recipient.strip().lower()
            if rec_clean in ["myself", "self", "me", "user"]:
                # Lookup user's own phone
                user_phone = await memory_manager.get_user_profile_value("phone") or await memory_manager.get_user_profile_value("phone_number")
                if user_phone:
                    clean_recipient = "".join([c for c in str(user_phone) if c.isdigit() or c == "+"])
            else:
                # Check if it contains digits directly
                digits = "".join([c for c in actual_recipient if c.isdigit() or c == "+"])
                if len(digits) >= 7:
                    clean_recipient = digits
                else:
                    # Look up contact name in memory (e.g. key="govardhan", key="mom")
                    contact_phone = await memory_manager.get_user_profile_value(rec_clean)
                    if contact_phone:
                        clean_recipient = "".join([c for c in str(contact_phone) if c.isdigit() or c == "+"])

        if clean_recipient:
            uri = f"whatsapp://send?phone={clean_recipient}&text={encoded_msg}"
            web_url = f"https://web.whatsapp.com/send?phone={clean_recipient}&text={encoded_msg}"
            msg_target = f"to {actual_recipient or clean_recipient}"
        else:
            uri = f"whatsapp://send?text={encoded_msg}"
            web_url = f"https://web.whatsapp.com/send?text={encoded_msg}"
            if actual_recipient and actual_recipient.lower() not in ["myself", "self", "me"]:
                msg_target = f"for {actual_recipient} (contact number not in memory, please select from WhatsApp)"
            else:
                msg_target = ""

        try:
            # Try native WhatsApp protocol
            try:
                os.startfile(uri)
            except Exception:
                try:
                    subprocess.Popen(f'start "" "{uri}"', shell=True)
                except Exception:
                    os.startfile(web_url)

            # Wait briefly and press enter if window focuses
            await asyncio.sleep(1.5)
            try:
                pyautogui.press("enter")
            except Exception:
                pass

            target = f"to {recipient}" if recipient else ""
            return ToolResult(
                success=True,
                data={"message": message, "recipient": recipient, "uri": uri},
                message=f"WhatsApp opened with message '{message}' {target}."
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Could not open WhatsApp: {str(e)}")

class TypeAndPressEnterTool(BaseTool):
    name = "type_and_press_enter"
    description = "Types text directly into the active window and presses Enter (e.g., to send a message or submit a prompt)."
    category = "Computer"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to type into the focused application"
            }
        },
        "required": ["text"]
    }

    async def execute(self, text: str, **kwargs) -> ToolResult:
        import asyncio
        try:
            await asyncio.sleep(0.5)
            pyautogui.write(text, interval=0.02)
            await asyncio.sleep(0.2)
            pyautogui.press("enter")
            return ToolResult(success=True, data={"text": text}, message=f"Typed '{text}' and pressed Enter.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

