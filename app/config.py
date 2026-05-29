"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (parent of app/)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central configuration for the Enterprise RAG application."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API keys
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")

    # Paths
    documents_dir: Path = Field(default=BASE_DIR / "documents")
    chroma_persist_dir: Path = Field(default=BASE_DIR / "chroma_db")

    # Chroma / RAG
    chroma_collection_name: str = Field(default="enterprise_rag")
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    retrieval_top_k: int = Field(default=5)

    # Embeddings
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2")

    # Gemini
    gemini_model: str = Field(default="gemini-2.0-flash")
    gemini_temperature: float = Field(default=0.2)

    # Upload limits
    max_upload_size_mb: int = Field(default=25)
    allowed_extensions: tuple[str, ...] = (".pdf",)

    # Chat history
    max_chat_history_messages: int = Field(default=20)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    def ensure_directories(self) -> None:
        """Create required directories if they do not exist."""
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    settings = Settings()
    settings.ensure_directories()
    return settings
