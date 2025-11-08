"""OCR reader responsible for extracting text from PDFs."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class OCRReader:
    """Extract text from PDF documents."""

    def extract_text(self, pdf_path: Path) -> str:
        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text.strip())
        text = "\n\n".join(part for part in pages if part)
        if not text.strip():
            raise ValueError("No text could be extracted from the provided PDF")
        return text
