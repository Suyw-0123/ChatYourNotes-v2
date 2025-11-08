"""Utility helpers for saving pipeline artifacts to disk."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple
from uuid import uuid4

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..config import Settings


class FileHandler:
    """Handle persistence of PDFs, extracted text, and summaries."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def generate_document_id(self) -> str:
        return uuid4().hex

    def save_pdf(self, file: FileStorage, document_id: str) -> Tuple[str, Path]:
        filename = secure_filename(file.filename or f"document-{document_id}.pdf")
        stored_name = f"{document_id}_{filename}" if filename else f"{document_id}.pdf"
        target = self._settings.pdf_dir / stored_name
        file.save(target)
        return stored_name, target

    def save_text(self, document_id: str, text: str) -> Path:
        target = self._settings.ocr_dir / f"{document_id}.txt"
        target.write_text(text, encoding="utf-8")
        return target

    def save_summary(self, document_id: str, summary: str) -> Path:
        target = self._settings.summary_dir / f"{document_id}.txt"
        target.write_text(summary, encoding="utf-8")
        return target
