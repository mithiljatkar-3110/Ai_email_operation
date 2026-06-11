from __future__ import annotations

import logging
from typing import TypedDict

from app.rag.embedding_service import embed_text
from app.rag.vector_store import VectorStore, get_vector_store

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 3


class RetrievedChunk(TypedDict):
    source_doc: str
    chunk_text: str
    similarity_score: float


class Retriever:
    """Retrieve relevant knowledge base chunks for a natural-language query."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> None:
        self.vector_store = vector_store or get_vector_store()
        self.top_k = top_k

    def _ensure_index_loaded(self) -> None:
        try:
            self.vector_store.index
            return
        except RuntimeError:
            pass

        if not self.vector_store.index_path.is_file():
            raise FileNotFoundError(
                f"FAISS index not found at {self.vector_store.index_path}. "
                "Build and save the index before retrieving."
            )

        self.vector_store.load_index()

    def retrieve(self, query: str, k: int | None = None) -> list[RetrievedChunk]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        self._ensure_index_loaded()
        top_k = k if k is not None else self.top_k

        logger.info("Retrieving top %s chunks for query", top_k)
        query_embedding = embed_text(query)
        results = self.vector_store.search(query_embedding, k=top_k)

        chunks: list[RetrievedChunk] = [
            {
                "source_doc": result["source_doc"],
                "chunk_text": result["chunk_text"],
                "similarity_score": result["similarity_score"],
            }
            for result in results
        ]

        logger.info("Retrieved %s chunks for query", len(chunks))
        return chunks


_default_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    global _default_retriever
    if _default_retriever is None:
        _default_retriever = Retriever()
    return _default_retriever


def retrieve(query: str, k: int = DEFAULT_TOP_K) -> list[RetrievedChunk]:
    return get_retriever().retrieve(query, k=k)
