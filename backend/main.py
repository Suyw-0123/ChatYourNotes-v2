"""WSGI entry-point used by Docker and local development."""

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
