"""Application factory for the ChatYourNotes backend."""

from flask import Flask
from flask_cors import CORS

from .config import Settings
from .api import api_bp
from .error_handlers import register_error_handlers
from .extensions import db
from .services.pipeline_service import PipelineService
from .services.vector_store import VectorStore


def create_app() -> Flask:
    """Create and configure the Flask application."""
    settings = Settings()
    settings.ensure_directories()

    app = Flask(__name__)
    app.config.update(settings.to_flask_config())
    app.config["APP_SETTINGS"] = settings

    CORS(app, resources={r"/api/*": {"origins": settings.cors_origins}})
    register_error_handlers(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    vector_store = VectorStore(settings)
    pipeline_service = PipelineService(settings, vector_store=vector_store)

    app.config["VECTOR_STORE"] = vector_store
    app.config["PIPELINE_SERVICE"] = pipeline_service

    app.register_blueprint(api_bp, url_prefix="/api")
    return app
