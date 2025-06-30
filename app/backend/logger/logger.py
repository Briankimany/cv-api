
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
import os
from app.backend.config.config import LoggerConfig ,APP_DATA_PATH

class CustomLogger:
    def __init__(self, config: LoggerConfig, level_map: Optional[dict] = None, 
                 max_bytes: int = 10485760, backup_count: int = 5):
        """
        Initialize a configured logger from a LoggerConfig instance.

        Args:
            config (LoggerConfig): Configuration for the logger.
            level_map (dict): Optional custom level mapping, defaults to logging module.
            max_bytes (int): Max file size for log rotation.
            backup_count (int): Number of rotated backups to keep.
        """
        level_map = level_map or {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }

        self.logger = logging.getLogger(config.name)
        self.logger.setLevel(level_map.get(config.level.upper(), logging.INFO))

        self.logger.handlers.clear()

        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        if config.stream:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if config.path:
            log_path = APP_DATA_PATH /config.path

            os.makedirs(os.path.dirname(log_path), exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)


 
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional extra data."""
        self._log_with_extras(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log informational message with optional extra data."""
        self._log_with_extras(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with optional extra data."""
        self._log_with_extras(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional extra data."""
        self._log_with_extras(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with optional extra data."""
        self._log_with_extras(logging.CRITICAL, message, kwargs)

    def _log_with_extras(self, level: int, message: str, extras: dict) -> None:
        """Internal method to handle logging with additional context."""
        if extras:
            self.logger.log(level, message, extra=extras)
        else:
            self.logger.log(level, message)

    def set_level(self, level: int) -> None:
        """Dynamically change the logging level."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)