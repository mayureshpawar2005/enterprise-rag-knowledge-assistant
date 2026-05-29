"""Health check endpoint."""

from fastapi import APIRouter, Depends

from app.models.schemas import HealthResponse
from app.dependencies import get_rag_service
from app.services.rag_service import RAGService

router = APIRouter(tags=["Health"])

APP_VERSION = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check(rag: RAGService = Depends(get_rag_service)) -> HealthResponse:
    """Return service health and dependency status."""
    status_info = rag.health_status()
    overall = (
        "healthy"
        if status_info["chroma_connected"] and status_info["gemini_configured"]
        else "degraded"
    )
    return HealthResponse(
        status=overall,
        version=APP_VERSION,
        chroma_connected=status_info["chroma_connected"],
        gemini_configured=status_info["gemini_configured"],
        documents_indexed=status_info["documents_indexed"],
    )
