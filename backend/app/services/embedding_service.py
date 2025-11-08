"""Sentence-transformer embeddings for vector similarity."""

from __future__ import annotations

import os
from typing import Iterable, List

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Wrap a sentence-transformers model for embedding generation."""

    def __init__(self, model_name: str | None = None):
        resolved = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self._model = SentenceTransformer(resolved)

    def embed_documents(self, texts: Iterable[str]) -> List[List[float]]:
        embeddings = self._model.encode(list(texts), show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self._model.encode(text, show_progress_bar=False, convert_to_numpy=True)
        return embedding.tolist()
