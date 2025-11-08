"""Vector store backed by ChromaDB for semantic search."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence

import chromadb

from ..config import Settings
from .embedding_service import EmbeddingService


class VectorStore:
    """Provide add/query operations for the document chunk vectors."""

    def __init__(self, settings: Settings, embedder: Optional[EmbeddingService] = None):
        self._settings = settings
        self._client = chromadb.PersistentClient(path=str(settings.vector_store_dir))
        self._collection = self._client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )
        self._embedder = embedder or EmbeddingService()

    def add_document(self, document_id: str, chunks: Iterable[str]) -> None:
        chunk_texts = list(chunks)
        if not chunk_texts:
            raise ValueError("Cannot index document without chunks")

        embeddings = self._embedder.embed_documents(chunk_texts)
        ids = [f"{document_id}_chunk_{index}" for index in range(len(chunk_texts))]
        metadatas = [{"document_id": document_id, "chunk_index": idx} for idx in range(len(chunk_texts))]
        self._collection.upsert(ids=ids, documents=chunk_texts, embeddings=embeddings, metadatas=metadatas)

    def delete_document(self, document_id: str) -> None:
        self._collection.delete(where={"document_id": document_id})

    def similarity_search(
        self,
        query: str,
        k: Optional[int] = None,
        document_ids: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, Any]]:
        top_k = k or 3
        query_embedding = self._embedder.embed_query(query)
        where = None
        if document_ids:
            where = {"document_id": {"$in": list(document_ids)}}
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

        matches: List[Dict[str, Any]] = []
        ids = results.get("ids") or [[]]
        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        distances = results.get("distances") or [[]]

        ids_row = ids[0] if ids else []
        documents_row = documents[0] if documents else []
        metadatas_row = metadatas[0] if metadatas else []
        distances_row = distances[0] if distances else []

        for idx, chunk_text in enumerate(documents_row):
            metadata = metadatas_row[idx] if idx < len(metadatas_row) else {}
            distance = distances_row[idx] if idx < len(distances_row) else None
            matches.append(
                {
                    "id": ids_row[idx] if idx < len(ids_row) else None,
                    "document_id": metadata.get("document_id"),
                    "chunk_index": metadata.get("chunk_index"),
                    "content": chunk_text,
                    "score": distance,
                }
            )
        return matches
