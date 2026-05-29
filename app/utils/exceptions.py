"""Custom application exceptions."""

from typing import Any, Optional


class RAGException(Exception):
    """Base exception for RAG application errors."""

    def __init__(self, message: str, detail: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


class ConfigurationError(RAGException):
    """Missing or invalid configuration (e.g. API keys)."""


class InvalidPDFError(RAGException):
    """Uploaded file is not a valid PDF."""


class EmptyDocumentError(RAGException):
    """PDF contains no extractable text."""


class VectorStoreError(RAGException):
    """ChromaDB or embedding persistence failure."""


class LLMError(RAGException):
    """Gemini API or LangChain LLM failure."""


class QuotaExceededError(LLMError):
    """Gemini API quota or rate limit exceeded (429 RESOURCE_EXHAUSTED)."""
