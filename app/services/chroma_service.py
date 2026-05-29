"""ChromaDB vector store operations."""

import uuid
from typing import Any, Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import Settings, get_settings
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.utils.exceptions import VectorStoreError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaService:
    """Manages persistent ChromaDB collection with LangChain-compatible operations."""

    def __init__(
        self,
        settings: Settings | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._embedding_service = embedding_service or get_embedding_service()
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection = None

    @property
    def client(self) -> chromadb.PersistentClient:
        if self._client is None:
            try:
                self._client = chromadb.PersistentClient(
                    path=str(self._settings.chroma_persist_dir),
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
            except Exception as exc:
                logger.error("ChromaDB client init failed: %s", exc)
                raise VectorStoreError(f"Failed to connect to ChromaDB: {exc}") from exc
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            try:
                self._collection = self.client.get_or_create_collection(
                    name=self._settings.chroma_collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception as exc:
                logger.error("ChromaDB collection error: %s", exc)
                raise VectorStoreError(f"Failed to access collection: {exc}") from exc
        return self._collection

    def _text_splitter(self) -> RecursiveCharacterTextSplitter:
        return RecursiveCharacterTextSplitter(
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def add_document(
        self,
        pages: List[Tuple[str, int]],
        document_name: str,
    ) -> Tuple[str, int]:
        """
        Split pages into chunks, embed, and store in ChromaDB.

        Returns:
            (document_id, number of chunks indexed)
        """
        document_id = str(uuid.uuid4())
        raw_docs: List[Document] = []
        for page_text, page_num in pages:
            raw_docs.append(
                Document(
                    page_content=page_text,
                    metadata={
                        "document_name": document_name,
                        "document_id": document_id,
                        "page": page_num,
                    },
                )
            )

        chunks = self._text_splitter().split_documents(raw_docs)
        if not chunks:
            raise VectorStoreError("Text splitting produced no chunks.")

        texts = [c.page_content for c in chunks]
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        for idx, chunk in enumerate(chunks):
            meta = dict(chunk.metadata)
            meta["chunk_index"] = idx
            metadatas.append(meta)
            ids.append(f"{document_id}_{idx}")

        try:
            embeddings = self._embedding_service.embed_documents(texts)
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
        except Exception as exc:
            logger.error("Failed to add vectors to ChromaDB: %s", exc)
            raise VectorStoreError(f"Failed to store embeddings: {exc}") from exc

        logger.info(
            "Indexed %d chunks for document %s (%s)",
            len(chunks),
            document_name,
            document_id,
        )
        return document_id, len(chunks)

    def similarity_search(
        self,
        query: str,
        top_k: int,
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve top-k similar chunks with relevance scores.

        Chroma returns distances; for cosine space, similarity ≈ 1 - distance.
        """
        try:
            query_embedding = self._embedding_service.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.error("Similarity search failed: %s", exc)
            raise VectorStoreError(f"Search failed: {exc}") from exc

        documents_out: List[Tuple[Document, float]] = []
        if not results or not results.get("documents") or not results["documents"][0]:
            return documents_out

        docs = results["documents"][0]
        metas = results["metadatas"][0] or []
        distances = results["distances"][0] or []

        for doc_text, meta, dist in zip(docs, metas, distances):
            # Convert distance to similarity score (cosine distance in [0, 2])
            similarity = max(0.0, 1.0 - float(dist))
            documents_out.append(
                (
                    Document(page_content=doc_text, metadata=meta or {}),
                    similarity,
                )
            )
        return documents_out

    def count_documents(self) -> int:
        """Return total number of chunks in the collection."""
        try:
            return self.collection.count()
        except Exception as exc:
            logger.error("ChromaDB count failed: %s", exc)
            raise VectorStoreError(f"Failed to count documents: {exc}") from exc

    def is_connected(self) -> bool:
        """Verify ChromaDB is accessible."""
        try:
            _ = self.collection.count()
            return True
        except Exception:
            return False
