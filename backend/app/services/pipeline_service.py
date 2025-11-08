"""End-to-end document ingestion pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from werkzeug.datastructures import FileStorage

from ..config import Settings
from ..models import Document
from .chunker import split_text
from .document_store import create_document, delete_by_document_id, get_by_document_id
from .file_handler import FileHandler
from .ocr_service import OCRReader
from .summarizer import generate_summary
from .vector_store import VectorStore


class PipelineService:
    """Run the document processing pipeline defined in the flowchart."""

    def __init__(self, settings: Settings, vector_store: Optional[VectorStore] = None):
        self._settings = settings
        self._file_handler = FileHandler(settings)
        self._ocr_reader = OCRReader()
        self._vector_store = vector_store or VectorStore(settings)

    def ingest(self, file: FileStorage) -> Document:
        if not file or not file.filename:
            raise ValueError("A PDF file is required")

        if not file.filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported")

        document_id = self._file_handler.generate_document_id()
        stored_pdf_name, pdf_path = self._file_handler.save_pdf(file, document_id)

        text_path = None
        summary_path = None
        try:
            extracted_text = self._ocr_reader.extract_text(pdf_path)
            text_path = self._file_handler.save_text(document_id, extracted_text)

            summary_text = generate_summary(extracted_text, model_name=self._settings.gemini_model)
            summary_path = self._file_handler.save_summary(document_id, summary_text)

            chunks = split_text(
                extracted_text,
                chunk_size=self._settings.chunk_size,
                overlap=self._settings.chunk_overlap,
            )
            if not chunks:
                chunks = [extracted_text]
            self._vector_store.add_document(document_id, chunks)

            summary_preview = summary_text[:500]
            document = create_document(
                document_id=document_id,
                original_filename=file.filename,
                stored_pdf=stored_pdf_name,
                text_path=text_path.name,
                summary_path=summary_path.name,
                summary_preview=summary_preview,
                chunk_count=len(chunks),
            )
            return document
        except Exception:
            self._vector_store.delete_document(document_id)
            for path in (pdf_path, text_path, summary_path):
                if isinstance(path, Path):
                    self._safe_unlink(path)
            raise

    def remove(self, document_id: str) -> bool:
        document = get_by_document_id(document_id)
        if not document:
            return False

        self._vector_store.delete_document(document_id)

        paths = (
            self._settings.pdf_dir / document.stored_pdf,
            self._settings.ocr_dir / document.text_path,
            self._settings.summary_dir / document.summary_path,
        )
        for path in paths:
            self._safe_unlink(path)

        return delete_by_document_id(document_id)

    @staticmethod
    def _safe_unlink(path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
