"""Route registration for the public API."""

from http import HTTPStatus
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, request

from ..config import Settings
from ..services import document_store
from ..services.pipeline_service import PipelineService
from ..services.qa_service import answer_question


def _get_settings() -> Settings:
    settings = current_app.config.get("APP_SETTINGS")
    if not settings:
        raise RuntimeError("Application settings are not configured")
    return settings


def _get_pipeline() -> PipelineService:
    pipeline = current_app.config.get("PIPELINE_SERVICE")
    if not pipeline:
        raise RuntimeError("Pipeline service is not initialized")
    return pipeline


def register_routes(bp: Blueprint) -> None:
    """Attach all API routes to the given blueprint."""

    @bp.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok"}), HTTPStatus.OK

    @bp.get("/documents")
    def list_documents() -> Any:
        documents = [document.to_dict() for document in document_store.list_documents()]
        return jsonify({"items": documents, "count": len(documents)}), HTTPStatus.OK

    @bp.post("/documents")
    def upload_document() -> Any:
        if "file" not in request.files:
            return jsonify({"error": "file field is required"}), HTTPStatus.BAD_REQUEST
        file = request.files["file"]

        try:
            document = _get_pipeline().ingest(file)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": f"Failed to process document: {exc}"}), HTTPStatus.INTERNAL_SERVER_ERROR

        return jsonify(document.to_dict()), HTTPStatus.CREATED

    @bp.delete("/documents/<string:document_id>")
    def delete_document(document_id: str) -> Any:
        removed = _get_pipeline().remove(document_id)
        if not removed:
            return jsonify({"error": "Document not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"status": "deleted", "document_id": document_id}), HTTPStatus.OK

    @bp.post("/qa")
    def ask_question() -> Any:
        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        question = (payload.get("question") or "").strip()
        document_id = payload.get("document_id")
        try:
            top_k = int(payload.get("top_k") or _get_settings().top_k)
        except (TypeError, ValueError):
            return jsonify({"error": "top_k must be an integer"}), HTTPStatus.BAD_REQUEST
        if top_k <= 0:
            return jsonify({"error": "top_k must be greater than zero"}), HTTPStatus.BAD_REQUEST

        if not question:
            return jsonify({"error": "Question is required"}), HTTPStatus.BAD_REQUEST

        vector_store = current_app.config.get("VECTOR_STORE")
        if not vector_store:
            return jsonify({"error": "Vector store is not initialized"}), HTTPStatus.INTERNAL_SERVER_ERROR

        if document_id:
            doc = document_store.get_by_document_id(document_id)
            if not doc:
                return jsonify({"error": "Document not found"}), HTTPStatus.NOT_FOUND

        document_filter = [document_id] if document_id else None
        matches = vector_store.similarity_search(question, k=top_k, document_ids=document_filter)
        contexts = [match["content"] for match in matches]

        if not contexts:
            return jsonify({"error": "No relevant context found"}), HTTPStatus.NOT_FOUND

        settings = _get_settings()
        try:
            answer = answer_question(question, contexts, model_name=settings.gemini_model)
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": f"Failed to generate answer: {exc}"}), HTTPStatus.INTERNAL_SERVER_ERROR

        return jsonify({"answer": answer, "matches": matches}), HTTPStatus.OK
