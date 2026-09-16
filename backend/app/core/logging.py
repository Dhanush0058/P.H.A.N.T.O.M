import logging
import re
import sys
from datetime import datetime
from typing import Any
from pathlib import Path
from backend.app.core.config import LOGS_DIR

# Sensitive patterns to scrub from logs
SENSITIVE_PATTERNS = [
    re.compile(r'(api[-_]?key|secret|token|password|auth|authorization)["\']?\s*[:=]\s*["\']?([^"\'\s]+)', re.IGNORECASE),
    re.compile(r'(Bearer\s+)([A-Za-z0-9_\-\.]{15,})', re.IGNORECASE),
    re.compile(r'([A-Za-z0-9]{32,})', re.IGNORECASE)
]

def mask_sensitive_data(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    masked = text
    for pattern in SENSITIVE_PATTERNS:
        masked = pattern.sub(r'\1: [REDACTED]', masked)
    return masked

class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        orig = super().format(record)
        return mask_sensitive_data(orig)

def setup_logger(name: str = "JARVIS") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_fmt = SafeFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_fmt)
        logger.addHandler(console_handler)

        log_file = LOGS_DIR / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = SafeFormatter(
            "%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s"
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()
