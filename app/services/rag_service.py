"""Orchestrates the full RAG pipeline: ingest and query."""

from typing import Optional

from fastapi import UploadFile

from app.config import Settings, get_settings
from app.models.schemas import AskResponse, SourceChunk, UploadResponse
from app.services.chat_history_service import ChatHistoryService
from app.services.chroma_service import ChromaService
from app.services.llm_service import LLMService, QUOTA_FALLBACK_MESSAGE
from app.services.pdf_service import PDFService
from app.utils.exceptions import InvalidPDFError, QuotaExceededError
from app.utils.logger import get_logger
from app.utils.validators import validate_pdf_upload

logger = get_logger(__name__)


class RAGService:
    """
    High-level RAG orchestrator.
    Coordinates PDF ingestion, vector search, and LLM answer generation.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        pdf_service: PDFService | None = None,
        chroma_service: ChromaService | None = None,
        llm_service: LLMService | None = None,
        chat_service: ChatHistoryService | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._pdf = pdf_service or PDFService()
        self._chroma = chroma_service or ChromaService()
        self._llm = llm_service or LLMService()
        self._chat = chat_service or ChatHistoryService()

    async def upload_pdf(self, file: UploadFile) -> UploadResponse:
        """Save PDF, extract text, chunk, embed, and store in ChromaDB."""
        safe_name = validate_pdf_upload(file, self._settings)
        dest_path = self._settings.documents_dir / safe_name

        # Read and enforce size limit
        content = await file.read()
        if len(content) > self._settings.max_upload_bytes:
            raise InvalidPDFError(
                f"File exceeds maximum size of {self._settings.max_upload_size_mb} MB."
            )
        if len(content) == 0:
            raise InvalidPDFError("Uploaded file is empty.")

        dest_path.write_bytes(content)
        logger.info("Saved upload: %s (%d bytes)", safe_name, len(content))

        pages = self._pdf.extract_text(dest_path)
        document_id, chunk_count = self._chroma.add_document(pages, safe_name)
        total = self._chroma.count_documents()

        return UploadResponse(
            message="Document uploaded and indexed successfully.",
            filename=safe_name,
            document_id=document_id,
            chunks_indexed=chunk_count,
            total_documents_in_store=total,
        )

    async def upload_multiple_pdfs(self, files: list[UploadFile]) -> list[UploadResponse]:
        """Index multiple PDF files in one request."""
        results: list[UploadResponse] = []
        for upload_file in files:
            results.append(await self.upload_pdf(upload_file))
        return results

    def ask(
        self,
        question: str,
        session_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> AskResponse:
        """Retrieve context, generate answer, return sources and optional session."""
        k = top_k or self._settings.retrieval_top_k
        session = self._chat.get_or_create_session(session_id)

        logger.info("Processing question (session=%s): %s", session, question[:80])

        retrieved = self._chroma.similarity_search(question, top_k=k)

        # Use prior turns when client sends an existing session_id
        history = (
            self._chat.get_langchain_messages(session) if session_id else None
        )

        fallback_mode = False
        try:
            answer = self._llm.generate_answer(
                question, retrieved, chat_history=history
            )
        except QuotaExceededError:
            logger.warning(
                "Gemini quota exceeded; serving retrieval fallback for session %s",
                session,
            )
            answer = QUOTA_FALLBACK_MESSAGE
            fallback_mode = True

        self._chat.append_exchange(session, question, answer)

        sources = [self._build_source_chunk(doc, score, idx) for idx, (doc, score) in enumerate(retrieved)]

        return AskResponse(
            answer=answer,
            sources=sources,
            session_id=session,
            question=question,
            fallback_mode=fallback_mode,
        )

    @staticmethod
    def _build_source_chunk(doc, score: float, rank: int) -> SourceChunk:
        meta = doc.metadata
        doc_name = meta.get("document_name", "unknown")
        chunk_index = meta.get("chunk_index", rank)
        page = meta.get("page")
        page_part = f", p. {page}" if page else ""
        citation = f"{doc_name}{page_part} [chunk {chunk_index}]"
        return SourceChunk(
            content=doc.page_content,
            document_name=doc_name,
            chunk_index=int(chunk_index) if chunk_index is not None else rank,
            page=int(page) if page is not None else None,
            relevance_score=round(score, 4),
            citation=citation,
        )

    def health_status(self) -> dict:
        """Collect health check fields."""
        chroma_ok = self._chroma.is_connected()
        gemini_ok = bool(
            self._settings.gemini_api_key and self._settings.gemini_api_key.strip()
        )
        try:
            doc_count = self._chroma.count_documents() if chroma_ok else 0
        except Exception:
            doc_count = 0

        return {
            "chroma_connected": chroma_ok,
            "gemini_configured": gemini_ok,
            "documents_indexed": doc_count,
        }

    def search(self, question: str, top_k: int = 5) -> list[SourceChunk]:
        """
        Debug retrieval: ChromaDB similarity search only (no Gemini).
        Returns the top-k matching document chunks.
        """
        logger.info("Search request (debug): %s", question[:80])
        retrieved = self._chroma.similarity_search(question, top_k=top_k)
        return [
            self._build_source_chunk(doc, score, idx)
            for idx, (doc, score) in enumerate(retrieved)
        ]
