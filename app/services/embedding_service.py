"""Embedding generation using sentence-transformers via LangChain."""

from functools import lru_cache
from typing import List

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import Settings, get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Wraps HuggingFace sentence-transformers for document and query embeddings."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._embeddings: Embeddings | None = None

    @property
    def embeddings(self) -> Embeddings:
        """Lazy-load embedding model (heavy on first use)."""
        if self._embeddings is None:
            logger.info(
                "Loading embedding model: %s", self._settings.embedding_model_name
            )
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self._settings.embedding_model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of document chunks."""
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a search query."""
        return self.embeddings.embed_query(text)


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Cached embedding service singleton."""
    return EmbeddingService()
