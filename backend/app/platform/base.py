from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path

class BasePlatform(ABC):
    @abstractmethod
    def open_application(self, app_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def close_application(self, process_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_running_processes(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_system_metrics(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def take_screenshot(self, save_path: Optional[Path] = None) -> Dict[str, Any]:
        pass
