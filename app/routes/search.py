"""Debug vector search endpoint (no LLM)."""

from fastapi import APIRouter, Depends

from app.dependencies import get_rag_service
from app.models.schemas import SearchRequest, SearchResponse
from app.services.rag_service import RAGService
from app.utils.logger import get_logger

router = APIRouter(tags=["Debug"])
logger = get_logger(__name__)

SEARCH_TOP_K = 5


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    body: SearchRequest,
    rag: RAGService = Depends(get_rag_service),
) -> SearchResponse:
    """
    Debug endpoint: run ChromaDB similarity search only.

    Does **not** call Gemini. Returns the top 5 retrieved document chunks.
    """
    question = body.question.strip()
    logger.info("Debug search: %s", question[:100])
    chunks = rag.search(question, top_k=SEARCH_TOP_K)
    return SearchResponse(retrieved_chunks=chunks)
