import io
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast
import unittest
from unittest.mock import patch

from flask import Flask
from werkzeug.datastructures import FileStorage

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import Settings
from app.extensions import db
from app.models import Document
from app.services.pipeline_service import PipelineService
from app.services.vector_store import VectorStore


_MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< >>\n%%EOF\n"


class FakeVectorStore:
    def __init__(self) -> None:
        self.added = []
        self.deleted = []

    def add_document(self, document_id: str, chunks) -> None:
        self.added.append((document_id, list(chunks)))

    def delete_document(self, document_id: str) -> None:
        self.deleted.append(document_id)


class PipelineServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.previous_data_dir = os.environ.get("DATA_DIR")
        os.environ["DATA_DIR"] = self.temp_dir.name

        self.settings = Settings()
        self.settings.ensure_directories()

        self.app = Flask(__name__)
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.app.config.update(
            SQLALCHEMY_DATABASE_URI=f"sqlite:///{self.database_path}",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.vector_store = FakeVectorStore()
        self.pipeline = PipelineService(
            self.settings,
            vector_store=cast(VectorStore, self.vector_store),
        )

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

        if self.previous_data_dir is not None:
            os.environ["DATA_DIR"] = self.previous_data_dir
        else:
            os.environ.pop("DATA_DIR", None)

        self.temp_dir.cleanup()

    @staticmethod
    def _make_upload(filename: str = "example.pdf") -> FileStorage:
        buffer = io.BytesIO(_MINIMAL_PDF)
        buffer.seek(0)
        return FileStorage(stream=buffer, filename=filename, content_type="application/pdf")

    def test_ingest_saves_files_and_metadata(self) -> None:
        upload = self._make_upload()

        with patch.object(self.pipeline._ocr_reader, "extract_text", return_value="Extracted body"), \
            patch("app.services.pipeline_service.generate_summary", return_value="Summary body"), \
            patch("app.services.pipeline_service.split_text", return_value=["chunk1", "chunk2"]):
            document = self.pipeline.ingest(upload)

        self.assertEqual(document.original_filename, "example.pdf")
        self.assertEqual(document.chunk_count, 2)
        self.assertEqual(len(self.vector_store.added), 1)
        doc_id, chunks = self.vector_store.added[0]
        self.assertEqual(doc_id, document.document_id)
        self.assertEqual(chunks, ["chunk1", "chunk2"])

        stored = Document.query.filter_by(document_id=document.document_id).first()
        self.assertIsNotNone(stored)
        self.assertTrue((self.settings.pdf_dir / stored.stored_pdf).exists())
        self.assertTrue((self.settings.ocr_dir / stored.text_path).exists())
        self.assertTrue((self.settings.summary_dir / stored.summary_path).exists())
        self.assertEqual(document.summary_preview, "Summary body"[:500])
        self.assertFalse(self.vector_store.deleted)

    def test_remove_cleans_up_artifacts(self) -> None:
        upload = self._make_upload("to-delete.pdf")

        with patch.object(self.pipeline._ocr_reader, "extract_text", return_value="Extracted body"), \
            patch("app.services.pipeline_service.generate_summary", return_value="Summary body"), \
            patch("app.services.pipeline_service.split_text", return_value=["chunkA"]):
            document = self.pipeline.ingest(upload)

        pdf_path = self.settings.pdf_dir / document.stored_pdf
        text_path = self.settings.ocr_dir / document.text_path
        summary_path = self.settings.summary_dir / document.summary_path

        self.assertTrue(pdf_path.exists())
        self.assertTrue(text_path.exists())
        self.assertTrue(summary_path.exists())

        removed = self.pipeline.remove(document.document_id)

        self.assertTrue(removed)
        self.assertFalse(pdf_path.exists())
        self.assertFalse(text_path.exists())
        self.assertFalse(summary_path.exists())
        self.assertIsNone(Document.query.filter_by(document_id=document.document_id).first())
        self.assertEqual(self.vector_store.deleted, [document.document_id])


if __name__ == "__main__":
    unittest.main()
