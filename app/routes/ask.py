"""Question-answering endpoint."""

from fastapi import APIRouter, Depends

from app.models.schemas import AskRequest, AskResponse
from app.dependencies import get_rag_service
from app.services.rag_service import RAGService
from app.utils.logger import get_logger

router = APIRouter(tags=["Q&A"])
logger = get_logger(__name__)


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    body: AskRequest,
    rag: RAGService = Depends(get_rag_service),
) -> AskResponse:
    """
    Ask a question against uploaded documents.
    Retrieves top-k chunks, sends context to Gemini, returns answer and sources.
    """
    logger.info("Ask request: %s", body.question[:100])
    return rag.ask(
        question=body.question.strip(),
        session_id=body.session_id,
        top_k=body.top_k,
    )
