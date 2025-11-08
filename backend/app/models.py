"""Database models for the ChatYourNotes backend."""

from datetime import datetime
from typing import Dict

from .extensions import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(64), unique=True, nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_pdf = db.Column(db.String(255), nullable=False)
    text_path = db.Column(db.String(255), nullable=False)
    summary_path = db.Column(db.String(255), nullable=False)
    summary_preview = db.Column(db.Text, nullable=True)
    chunk_count = db.Column(db.Integer, nullable=False, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, object]:
        """Serialize the document metadata for API responses."""
        return {
            "document_id": self.document_id,
            "original_filename": self.original_filename,
            "stored_pdf": self.stored_pdf,
            "text_path": self.text_path,
            "summary_path": self.summary_path,
            "summary_preview": self.summary_preview,
            "chunk_count": self.chunk_count,
            "uploaded_at": self.uploaded_at.isoformat(),
        }
