
import logging
import sys
from typing import Any, Dict, Optional
import structlog

# Antirez style: The Observability class is responsible for setting up 
# the logging infrastructure. We use structlog to ensure that logs 
# are machine-readable (JSON) for analysis and human-readable for debugging.
class Observability:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self._setup_logging()

    # Configure the logging processors and formatters.
    # If debug is enabled, we output colored logs to the console.
    # Otherwise, we default to JSON logging for potential external ingestion.
    def _setup_logging(self) -> None:
        shared_processors = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]

        if self.debug:
            processors = shared_processors + [
                structlog.dev.ConsoleRenderer()
            ]
            level = logging.DEBUG
        else:
            processors = shared_processors + [
                structlog.processors.JSONRenderer()
            ]
            level = logging.INFO

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Standard library logging integration
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stderr,
            level=level,
        )

    # Helper method to get a logger instance for a specific component.
    # This ensures consistency across the application.
    def get_logger(self, name: str) -> structlog.stdlib.BoundLogger:
        return structlog.get_logger(name)

# Global accessibility for simple usage if needed, 
# though instantiation is preferred in main.
# _obs = Observability(debug=True)
# logger = _obs.get_logger("global")
