"""Input validation helpers."""

from pathlib import Path

from fastapi import UploadFile

from app.config import Settings
from app.utils.exceptions import InvalidPDFError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_pdf_upload(file: UploadFile, settings: Settings) -> str:
    """
    Validate uploaded file is a PDF within size limits.
    Returns the safe filename to use on disk.
    """
    if not file.filename:
        raise InvalidPDFError("Filename is required.")

    if not file.content_type:
        logger.debug("No content-type for %s; validating by extension only.", file.filename)
    elif file.content_type not in (
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    ):
        # Some browsers send octet-stream for PDFs; reject clearly non-PDF types
        if not file.content_type.startswith("application/"):
            raise InvalidPDFError(
                f"Invalid content type '{file.content_type}'. Only PDF files are supported."
            )

    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise InvalidPDFError(
            f"Invalid file type '{suffix}'. Allowed: {', '.join(settings.allowed_extensions)}"
        )

    # Sanitize filename (basename only)
    safe_name = Path(file.filename).name
    if not safe_name.endswith(".pdf"):
        raise InvalidPDFError("Only PDF files are supported.")

    return safe_name
