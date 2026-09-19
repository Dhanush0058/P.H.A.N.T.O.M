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
                "description": "Optional contact name (e.g. 'Govardhan', 'Daddy', 'myself') or phone number with country code (e.g. '+919876543210')"
            }
        },
        "required": ["message"]
    }

    async def execute(self, message: Optional[str] = None, recipient: Optional[str] = None, **kwargs) -> ToolResult:
        import urllib.parse
        import os
        import asyncio
        import subprocess
        from backend.app.memory.manager import memory_manager

        actual_message = str(message or kwargs.get("text") or kwargs.get("msg") or kwargs.get("body") or "Hi").strip()
        encoded_msg = urllib.parse.quote(actual_message)
        clean_recipient = ""
        actual_recipient = str(recipient or kwargs.get("to") or kwargs.get("phone") or kwargs.get("contact") or "").strip()

        if actual_recipient:
            rec_clean = actual_recipient.lower()
            if rec_clean in ["myself", "self", "me", "user"]:
                user_phone = await memory_manager.get_user_profile_value("phone") or await memory_manager.get_user_profile_value("phone_number")
                if user_phone:
                    clean_recipient = "".join([c for c in str(user_phone) if c.isdigit() or c == "+"])
            else:
                digits = "".join([c for c in actual_recipient if c.isdigit() or c == "+"])
                if len(digits) >= 7:
                    clean_recipient = digits
                else:
                    # Look up contact name in memory (e.g. 'govardhan', 'contact_govardhan', 'daddy', 'mom')
                    contact_phone = (
                        await memory_manager.get_user_profile_value(rec_clean) or
                        await memory_manager.get_user_profile_value(f"contact_{rec_clean}") or
                        await memory_manager.long_term.recall(rec_clean) or
                        await memory_manager.long_term.recall(f"contact_{rec_clean}")
                    )
                    if contact_phone:
                        clean_recipient = "".join([c for c in str(contact_phone) if c.isdigit() or c == "+"])

        try:
            if clean_recipient:
                # Direct URI with phone number
                uri = f"whatsapp://send?phone={clean_recipient}&text={encoded_msg}"
                web_url = f"https://web.whatsapp.com/send?phone={clean_recipient}&text={encoded_msg}"
                try:
                    os.startfile(uri)
                except Exception:
                    try:
                        subprocess.Popen(f'start "" "{uri}"', shell=True)
                    except Exception:
                        os.startfile(web_url)

                await asyncio.sleep(1.8)
                try:
                    pyautogui.press("enter")
                except Exception:
                    pass

                target_label = f"to {actual_recipient} ({clean_recipient})" if actual_recipient and actual_recipient != clean_recipient else f"to {clean_recipient}"
                return ToolResult(
                    success=True,
                    data={"message": actual_message, "recipient": clean_recipient, "uri": uri},
                    message=f"WhatsApp opened with message '{actual_message}' {target_label}."
                )
            elif actual_recipient and actual_recipient.lower() not in ["myself", "self", "me"]:
                # Contact name specified but no phone stored: open WhatsApp, search contact name, type message and send!
                try:
                    os.startfile("whatsapp:")
                except Exception:
                    try:
                        subprocess.Popen('start "" "whatsapp:"', shell=True)
                    except Exception:
                        os.startfile("https://web.whatsapp.com")

                await asyncio.sleep(2.0)
                try:
                    # Focus search in WhatsApp desktop with Ctrl+F
                    pyautogui.hotkey("ctrl", "f")
                    await asyncio.sleep(0.5)
                    pyautogui.write(actual_recipient, interval=0.03)
                    await asyncio.sleep(1.0)
                    pyautogui.press("enter")
                    await asyncio.sleep(0.8)
                    # Type message and send
                    pyautogui.write(actual_message, interval=0.03)
                    await asyncio.sleep(0.3)
                    pyautogui.press("enter")
                except Exception as ui_err:
                    pass

                return ToolResult(
                    success=True,
                    data={"message": actual_message, "recipient": actual_recipient},
                    message=f"WhatsApp opened, searched for '{actual_recipient}', and sent '{actual_message}'."
                )
            else:
                # General WhatsApp send
                uri = f"whatsapp://send?text={encoded_msg}"
                try:
                    os.startfile(uri)
                except Exception:
                    subprocess.Popen(f'start "" "{uri}"', shell=True)
                await asyncio.sleep(1.5)
                try:
                    pyautogui.press("enter")
                except Exception:
                    pass
                return ToolResult(
                    success=True,
                    data={"message": actual_message},
                    message=f"WhatsApp opened with message '{actual_message}'."
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

class MediaVolumeControlTool(BaseTool):
    name = "media_volume_control"
    description = "Controls Windows system audio volume, mute/unmute, and media playback (play/pause, next track, previous track)."
    category = "Computer"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["volume_up", "volume_down", "mute", "unmute", "play_pause", "next_track", "prev_track"],
                "description": "Audio or media action to perform"
            },
            "steps": {
                "type": "integer",
                "description": "Number of volume steps (default: 5 for ~10% change)"
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str, steps: int = 5, **kwargs) -> ToolResult:
        act = action.lower().strip()
        try:
            if act in ["volume_up", "up", "increase", "louder"]:
                pyautogui.press("volumeup", presses=max(1, min(steps, 25)))
                return ToolResult(success=True, message="Volume increased.")
            elif act in ["volume_down", "down", "decrease", "softer", "quieter"]:
                pyautogui.press("volumedown", presses=max(1, min(steps, 25)))
                return ToolResult(success=True, message="Volume decreased.")
            elif act in ["mute", "unmute", "toggle_mute"]:
                pyautogui.press("volumemute")
                return ToolResult(success=True, message="Audio mute toggled.")
            elif act in ["play_pause", "play", "pause", "toggle_playback"]:
                pyautogui.press("playpause")
                return ToolResult(success=True, message="Media playback toggled.")
            elif act in ["next_track", "next", "skip"]:
                pyautogui.press("nexttrack")
                return ToolResult(success=True, message="Skipped to next media track.")
            elif act in ["prev_track", "previous", "previous_track", "back"]:
                pyautogui.press("prevtrack")
                return ToolResult(success=True, message="Returned to previous media track.")
            else:
                return ToolResult(success=False, error=f"Unknown media action: '{action}'. Supported: volume_up, volume_down, mute, play_pause, next_track, prev_track")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class ClipboardTool(BaseTool):
    name = "clipboard_control"
    description = "Reads from or writes text to the Windows system clipboard."
    category = "Computer"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get", "set", "clear"],
                "description": "'get' to read copied clipboard text, 'set' to copy text to clipboard, 'clear' to empty"
            },
            "text": {
                "type": "string",
                "description": "Text to write to clipboard (required if action is 'set')"
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str, text: Optional[str] = None, **kwargs) -> ToolResult:
        import pyperclip
        act = action.lower().strip()
        try:
            if act in ["get", "read", "paste"]:
                content = pyperclip.paste()
                return ToolResult(
                    success=True,
                    data={"clipboard": content},
                    message=f"Clipboard content: '{content[:200]}...'" if len(content) > 200 else f"Clipboard content: '{content}'"
                )
            elif act in ["set", "copy", "write"]:
                val = text or kwargs.get("content") or ""
                pyperclip.copy(val)
                return ToolResult(success=True, message=f"Copied text to clipboard ({len(val)} characters).")
            elif act in ["clear", "empty"]:
                pyperclip.copy("")
                return ToolResult(success=True, message="Clipboard cleared.")
            else:
                return ToolResult(success=False, error=f"Unknown clipboard action: '{action}'")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


