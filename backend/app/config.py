"""Configuration helpers for the Flask backend."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple
import os


def _parse_origins(raw: str) -> Tuple[str, ...]:
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip()) or ("*",)


@dataclass
class Settings:
    """Read configuration from environment variables with sane defaults."""

    _root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    data_dir: Path = field(init=False)
    pdf_dir: Path = field(init=False)
    ocr_dir: Path = field(init=False)
    summary_dir: Path = field(init=False)
    vector_store_dir: Path = field(init=False)
    metadata_dir: Path = field(init=False)
    cors_origins: Tuple[str, ...] = field(default_factory=lambda: _parse_origins(os.getenv("CORS_ORIGINS", "*")))
    debug: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1200"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    top_k: int = int(os.getenv("TOP_K", "3"))
    mysql_user: str = os.getenv("MYSQL_USER", "chat_user")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "chat_password")
    mysql_host: str = os.getenv("MYSQL_HOST", "db")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_database: str = os.getenv("MYSQL_DATABASE", "chatyournotes")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def __post_init__(self) -> None:
        base_data = Path(os.getenv("DATA_DIR", self._root / "data"))
        self.data_dir = base_data
        self.pdf_dir = base_data / "pdfs"
        self.ocr_dir = base_data / "ocr_texts"
        self.summary_dir = base_data / "summaries"
        self.vector_store_dir = base_data / "vector_store"
        self.metadata_dir = base_data / "metadata"

    def ensure_directories(self) -> None:
        """Ensure the data folder hierarchy exists."""
        for path in (
            self.data_dir,
            self.pdf_dir,
            self.ocr_dir,
            self.summary_dir,
            self.vector_store_dir,
            self.metadata_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def to_flask_config(self) -> Dict[str, object]:
        """Map settings to Flask configuration keys."""
        return {
            "JSON_SORT_KEYS": False,
            "ENV": "development" if self.debug else "production",
            "SQLALCHEMY_DATABASE_URI": self.database_uri,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }

    @property
    def database_uri(self) -> str:
        """Construct the SQLAlchemy URI for the MySQL database."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )
