import subprocess
import os
import psutil
import pyautogui
from PIL import Image
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from backend.app.platform.base import BasePlatform
from backend.app.core.config import settings, DATA_DIR
from backend.app.core.logging import logger

class WindowsPlatform(BasePlatform):
    def __init__(self):
        # Configure pyautogui safety
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

    def open_application(self, app_name: str) -> Dict[str, Any]:
        app_key = app_name.lower().strip()
        command = settings.APP_ALIASES.get(app_key, app_key)
        try:
            logger.info(f"Launching Windows application: {app_name} -> {command}")
            # If it's a URI protocol scheme (whatsapp:, spotify:, ms-settings:) or web URL
            if command.endswith(":") or command.startswith("http://") or command.startswith("https://"):
                os.startfile(command)
            else:
                try:
                    os.startfile(command)
                except Exception:
                    subprocess.Popen(f'start "" "{command}"', shell=True)
            return {
                "success": True,
                "app_name": app_name,
                "command": command,
                "message": f"Successfully launched '{app_name}'."
            }
        except Exception as e:
            logger.error(f"Failed to launch application '{app_name}': {str(e)}")
            return {
                "success": False,
                "app_name": app_name,
                "error": str(e)
            }

    def close_application(self, process_name: str) -> Dict[str, Any]:
        terminated = []
        target = process_name.lower().replace(".exe", "")
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                if target in pname:
                    proc.terminate()
                    terminated.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if terminated:
            return {"success": True, "terminated": terminated, "message": f"Terminated {len(terminated)} instance(s) of '{process_name}'."}
        return {"success": False, "error": f"No active process matched '{process_name}'."}

    def get_running_processes(self) -> List[Dict[str, Any]]:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                if info['memory_percent'] and info['memory_percent'] > 0.1:
                    processes.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "cpu": round(info['cpu_percent'] or 0, 1),
                        "memory_percent": round(info['memory_percent'] or 0, 1),
                        "status": info['status']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        return processes[:25]

    def get_system_metrics(self) -> Dict[str, Any]:
        cpu_pct = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        net = psutil.net_io_counters()
        battery = psutil.sensors_battery()

        return {
            "os": "Windows",
            "cpu": {
                "usage_percent": cpu_pct,
                "cores": psutil.cpu_count(logical=True),
                "freq_mhz": round(cpu_freq.current if cpu_freq else 0, 1)
            },
            "memory": {
                "total_gb": round(mem.total / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "free_gb": round(mem.available / (1024**3), 2),
                "percent": mem.percent
            },
            "disk": {
                "drive": "C:",
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            },
            "network": {
                "bytes_sent_mb": round(net.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net.bytes_recv / (1024**2), 2)
            },
            "battery": {
                "percent": battery.percent if battery else None,
                "power_plugged": battery.power_plugged if battery else True
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    def take_screenshot(self, save_path: Optional[Path] = None) -> Dict[str, Any]:
        try:
            screenshots_dir = DATA_DIR / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            if save_path is None:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                save_path = screenshots_dir / filename

            img = pyautogui.screenshot()
            img.save(str(save_path))
            return {
                "success": True,
                "path": str(save_path),
                "width": img.width,
                "height": img.height,
                "message": f"Screenshot saved to {save_path.name}"
            }
        except Exception as e:
            logger.error(f"Screenshot capture failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

windows_platform = WindowsPlatform()
