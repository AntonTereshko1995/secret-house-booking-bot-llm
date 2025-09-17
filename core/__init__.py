"""
Ядро приложения (Core Layer)

Contains core configuration, logging, and utilities.
"""

from .config import settings, Settings
from .logging import setup_logging

__all__ = [
    "settings",
    "Settings", 
    "setup_logging",
]
