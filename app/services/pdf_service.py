"""PDF text extraction service."""

from pathlib import Path
from typing import List, Tuple

from pypdf import PdfReader

from app.utils.exceptions import EmptyDocumentError, InvalidPDFError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFService:
    """Extracts text from PDF documents with page metadata."""

    def extract_text(self, file_path: Path) -> List[Tuple[str, int]]:
        """
        Extract text from each page of a PDF.

        Returns:
            List of (page_text, page_number) tuples. Page numbers are 1-based.
        """
        if not file_path.exists():
            raise InvalidPDFError(f"File not found: {file_path}")

        try:
            reader = PdfReader(str(file_path))
        except Exception as exc:
            logger.error("Failed to read PDF %s: %s", file_path, exc)
            raise InvalidPDFError(f"Could not read PDF: {exc}") from exc

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise InvalidPDFError("PDF is encrypted and cannot be decrypted.")

        pages: List[Tuple[str, int]] = []
        for i, page in enumerate(reader.pages):
            try:
                text = (page.extract_text() or "").strip()
            except Exception as exc:
                logger.warning("Page %d extraction failed: %s", i + 1, exc)
                text = ""
            if text:
                pages.append((text, i + 1))

        if not pages:
            raise EmptyDocumentError(
                "No extractable text found in PDF. The document may be scanned images only."
            )

        logger.info("Extracted %d pages from %s", len(pages), file_path.name)
        return pages
