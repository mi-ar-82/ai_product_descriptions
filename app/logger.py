# File: app/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

class LoggingConfigurator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._configured = False

    def configure_logging(
        self,
        enable: bool = True,
        log_level: int = logging.INFO,
        max_bytes: int = 5*1024*1024,
        backup_count: int = 3
    ):
        if not enable or self._configured:
            return

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                self._create_console_handler(),
                self._create_file_handler(max_bytes, backup_count)
            ]
        )
        self._configured = True
        print(f"Debug: Logging configured with enable={enable}")
        print(f"Debug: Handler types: {[type(h) for h in self.logger.handlers]}")

    def _create_console_handler(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        ))
        return handler

    def _create_file_handler(self, max_bytes, backup_count):
        handler = RotatingFileHandler(
            'app.log',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(process)d] [%(levelname)s] %(message)s'
        ))
        return handler

logging_configurator = LoggingConfigurator()
