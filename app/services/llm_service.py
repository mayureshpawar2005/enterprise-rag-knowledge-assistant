"""Google Gemini LLM integration via LangChain."""

from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import Settings, get_settings
from app.utils.exceptions import ConfigurationError, LLMError, QuotaExceededError
from app.utils.llm_errors import is_gemini_quota_exhausted
from app.utils.logger import get_logger

logger = get_logger(__name__)

QUOTA_FALLBACK_MESSAGE = (
    "The Gemini API quota has been exceeded, so a generated answer is not available "
    "right now. Please try again later or review your Google AI Studio quota and billing. "
    "The most relevant passages from your uploaded documents are included in the "
    "sources below and may still help answer your question."
)

SYSTEM_PROMPT = """You are an Enterprise Knowledge Assistant. Answer questions using ONLY the provided context from uploaded documents.

Rules:
1. Base your answer strictly on the context below. If the context does not contain enough information, say you cannot find that information in the uploaded documents.
2. Be accurate, concise, and professional.
3. When relevant, reference which source document the information comes from.
4. Do not invent facts or use outside knowledge beyond the context.

Context from documents:
{context}
"""


class LLMService:
    """Generates answers using Google Gemini with retrieved context."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._llm: Optional[ChatGoogleGenerativeAI] = None

    def _validate_api_key(self) -> None:
        if not self._settings.gemini_api_key or not self._settings.gemini_api_key.strip():
            raise ConfigurationError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        if self._llm is None:
            self._validate_api_key()
            self._llm = ChatGoogleGenerativeAI(
                model=self._settings.gemini_model,
                google_api_key=self._settings.gemini_api_key,
                temperature=self._settings.gemini_temperature,
            )
        return self._llm

    @staticmethod
    def _format_context(chunks: List[tuple[Document, float]]) -> str:
        """Build context string from retrieved chunks with citations."""
        parts: List[str] = []
        for i, (doc, score) in enumerate(chunks, start=1):
            meta = doc.metadata
            doc_name = meta.get("document_name", "unknown")
            page = meta.get("page")
            page_str = f", page {page}" if page else ""
            parts.append(
                f"[Source {i}] Document: {doc_name}{page_str} (relevance: {score:.2f})\n"
                f"{doc.page_content}\n"
            )
        return "\n---\n".join(parts)

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: List[tuple[Document, float]],
        chat_history: Optional[List[BaseMessage]] = None,
    ) -> str:
        """Send question and context to Gemini and return the answer."""
        if not retrieved_chunks:
            return (
                "I could not find any relevant information in the uploaded documents "
                "to answer your question. Please upload relevant PDFs or rephrase your question."
            )

        context = self._format_context(retrieved_chunks)
        system_content = SYSTEM_PROMPT.format(context=context)

        messages: List[BaseMessage] = [SystemMessage(content=system_content)]

        if chat_history:
            messages.extend(chat_history)

        messages.append(HumanMessage(content=question))

        try:
            response = self.llm.invoke(messages)
            content = response.content
            if isinstance(content, list):
                # Multimodal response parts
                text_parts = [
                    p.get("text", "") if isinstance(p, dict) else str(p)
                    for p in content
                ]
                answer = "".join(text_parts).strip()
            else:
                answer = (content or "").strip()
            if not answer:
                raise LLMError("Gemini returned an empty response.")
            logger.info("Generated answer for question (len=%d)", len(question))
            return answer
        except ConfigurationError:
            raise
        except QuotaExceededError:
            raise
        except Exception as exc:
            if is_gemini_quota_exhausted(exc):
                logger.warning("Gemini quota exceeded (429 RESOURCE_EXHAUSTED)")
                raise QuotaExceededError(
                    "Gemini API quota exceeded (429 RESOURCE_EXHAUSTED)."
                ) from exc
            logger.error("Gemini API error: %s", exc)
            raise LLMError(f"Failed to generate answer: {exc}") from exc
