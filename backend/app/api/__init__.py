"""Blueprint definition for the public API."""

from flask import Blueprint

from .routes import register_routes

api_bp = Blueprint("api", __name__)
register_routes(api_bp)
