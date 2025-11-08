"""Orchestrates the full document ingestion and QA pipeline."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Optional

from werkzeug.datastructures import FileStorage

from ..config import Settings
from .chunker import split_text
from .document_store import DocumentStore
from .file_handler import FileHandler
from .ocr_service import OCRReader
from .qa_service import answer_question
from .summarizer import generate_summary
from .vector_store import VectorStore


class Pipeline:
    """Coordinate processing steps for document ingestion and question answering."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._file_handler = FileHandler(settings)
        self._ocr = OCRReader()
        self._vector_store = VectorStore(settings)
        self._documents = DocumentStore(settings)

    def ingest_document(self, upload: FileStorage) -> Dict:
        document_id = self._file_handler.generate_document_id()
        stored_name, pdf_path = self._file_handler.save_pdf(upload, document_id)

        extracted_text = self._ocr.extract_text(pdf_path)
        text_path = self._file_handler.save_text(document_id, extracted_text)

        chunks = split_text(
            extracted_text,
            chunk_size=self._settings.chunk_size,
            overlap=self._settings.chunk_overlap,
        )
        self._vector_store.add_document(document_id, chunks)

        summary = generate_summary(extracted_text)
        summary_path = self._file_handler.save_summary(document_id, summary)

        metadata = {
            "id": document_id,
            "original_filename": upload.filename,
            "stored_filename": stored_name,
            "pdf_path": str(pdf_path.relative_to(self._settings.data_dir)),
            "text_path": str(text_path.relative_to(self._settings.data_dir)),
            "summary_path": str(summary_path.relative_to(self._settings.data_dir)),
            "chunk_count": len(chunks),
        }
        self._documents.upsert(metadata)
        return metadata

    def list_documents(self) -> List[Dict]:
        return self._documents.list_documents()

    def retrieve_document(self, document_id: str) -> Optional[Dict]:
        return self._documents.get(document_id)

    def answer(self, question: str, top_k: Optional[int] = None) -> Dict:
        matches = self._vector_store.similarity_search(question, k=top_k or self._settings.top_k)
        contexts = [match["content"] for match in matches]
        response = answer_question(question, contexts)
        return {"answer": response, "matches": matches}
