"""Document upload endpoint."""

from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies import get_rag_service
from app.models.schemas import UploadResponse
from app.services.rag_service import RAGService
from app.utils.exceptions import InvalidPDFError
from app.utils.logger import get_logger

router = APIRouter(tags=["Documents"])
logger = get_logger(__name__)


@router.post(
    "/upload",
    response_model=list[UploadResponse],
    summary="Upload PDF documents",
    description=(
        "Upload one or more **PDF** files using multipart form data. "
        "Each file is extracted, chunked, embedded, and indexed in ChromaDB."
    ),
    response_description="Indexing result for each uploaded PDF.",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["files"],
                        "properties": {
                            "files": {
                                "type": "array",
                                "description": "One or more PDF files (.pdf)",
                                "items": {
                                    "type": "string",
                                    "format": "binary",
                                },
                            },
                        },
                    },
                },
            },
        },
    },
)
async def upload_documents(
    files: list[UploadFile] = File(
        ...,
        description="One or more PDF files (.pdf)",
        media_type="application/pdf",
    ),
    rag: RAGService = Depends(get_rag_service),
) -> list[UploadResponse]:
    """
    Accept PDF uploads via multipart/form-data.

    - **files**: Select one or more `.pdf` files (Swagger: **Choose File**).
    """
    if not files:
        raise InvalidPDFError("At least one PDF file is required.")

    logger.info("Upload request: %d file(s)", len(files))

    results: list[UploadResponse] = []
    for upload_file in files:
        results.append(await rag.upload_pdf(upload_file))
    return results
