"""Centralized error handlers for predictable API responses."""

from flask import Flask, jsonify


def register_error_handlers(app: Flask) -> None:
    """Register common error handlers on the given app."""

    @app.errorhandler(404)
    def handle_not_found(_: Exception):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_server_error(error: Exception):
        app.logger.exception("Unexpected server error", exc_info=error)
        return jsonify({"error": "Internal server error"}), 500
