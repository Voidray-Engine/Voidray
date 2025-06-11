"""
VoidRay Engine Logger
Professional logging system for the engine.
"""

import logging
import sys
from typing import Optional
from datetime import datetime


class EngineLogger:
    """
    Professional logging system for the VoidRay engine.
    """

    def __init__(self, name: str = "VoidRay", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.current_level = level

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # File handler with proper error handling
        file_handler = None
        try:
            import os
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler('logs/voidray_engine.log')
            file_handler.setLevel(logging.DEBUG)
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
            file_handler = None

        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler.setFormatter(formatter)
        if file_handler:
            file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        if file_handler:
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)

    def engine_start(self, width: int, height: int, fps: int):
        """Log engine startup information."""
        self.info(f"VoidRay Engine starting - Resolution: {width}x{height}, Target FPS: {fps}")

    def engine_stop(self):
        """Log engine shutdown."""
        self.info("VoidRay Engine shutting down")

    def scene_change(self, old_scene: str, new_scene: str):
        """Log scene change."""
        self.info(f"Scene transition: {old_scene} -> {new_scene}")

    def performance_warning(self, fps: float, target_fps: int):
        """Log performance warning."""
        self.warning(f"Performance issue: FPS {fps:.1f} (target: {target_fps})")

    def physics_optimization(self, removed_count: int):
        """Log physics optimization."""
        self.info(f"Physics optimization: Removed {removed_count} inactive colliders")
    
    def set_log_level(self, level: int):
        """Set the logging level."""
        self.logger.setLevel(level)
        self.current_level = level
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(logging.DEBUG)
            else:
                handler.setLevel(level)
    
    def get_log_level(self) -> int:
        """Get the current logging level."""
        return self.current_level


# Global logger instance
engine_logger = EngineLogger()