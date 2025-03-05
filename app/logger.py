# app/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

class LoggingConfigurator:
    def __init__(self):
        self.logger = logging.getLogger("app")
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

        # Clear existing handlers
        self.logger.handlers = []

        # Create handlers with proper encoding
        handlers = [
            self._create_console_handler(),
            self._create_file_handler(max_bytes, backup_count)
        ]

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=handlers,
            force=True  # Override existing configuration
        )

        # Windows-specific encoding fixes
        if sys.platform == "win32":
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')

        self._configured = True

    def _create_console_handler(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        ))
        handler.encoding = 'utf-8'
        handler.addFilter(SecurityFilter())
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

class SecurityFilter(logging.Filter):
    def filter(self, record):
        record.msg = self._sanitize(record.msg)
        return True

    def _sanitize(self, msg):
        return str(msg).replace('\n', '\\n').replace('\r', '\\r')

logging_configurator = LoggingConfigurator()
