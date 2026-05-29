"""Centralized logging configuration."""

import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a consistent format."""
    root = logging.getLogger()
    if root.handlers:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name or "enterprise_rag")
