"""Persist document metadata in the relational database."""

from __future__ import annotations

from typing import List, Optional

from ..extensions import db
from ..models import Document


def create_document(
    *,
    document_id: str,
    original_filename: str,
    stored_pdf: str,
    text_path: str,
    summary_path: str,
    summary_preview: str,
    chunk_count: int,
) -> Document:
    document = Document(
        document_id=document_id,
        original_filename=original_filename,
        stored_pdf=stored_pdf,
        text_path=text_path,
        summary_path=summary_path,
        summary_preview=summary_preview,
        chunk_count=chunk_count,
    )
    db.session.add(document)
    db.session.commit()
    return document


def list_documents() -> List[Document]:
    return Document.query.order_by(Document.uploaded_at.desc()).all()


def get_by_document_id(document_id: str) -> Optional[Document]:
    return Document.query.filter_by(document_id=document_id).first()


def delete_by_document_id(document_id: str) -> bool:
    document = get_by_document_id(document_id)
    if not document:
        return False
    db.session.delete(document)
    db.session.commit()
    return True
