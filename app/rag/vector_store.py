from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TypedDict

import faiss
import numpy as np
from numpy.typing import NDArray

from app.rag.chunker import DocumentChunk

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORAGE_DIR = PROJECT_ROOT / "storage"
DEFAULT_INDEX_PATH = STORAGE_DIR / "faiss_index.bin"
DEFAULT_METADATA_PATH = STORAGE_DIR / "faiss_metadata.json"
EMBEDDING_DIMENSION = 384


class ChunkMetadata(TypedDict):
    source_doc: str
    chunk_text: str


class SearchResult(TypedDict):
    source_doc: str
    chunk_text: str
    distance: float
    similarity_score: float
    index: int


class VectorStore:
    """FAISS IndexFlatL2 vector store with persisted chunk metadata."""

    def __init__(
        self,
        dimension: int = EMBEDDING_DIMENSION,
        index_path: Path | str = DEFAULT_INDEX_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
    ) -> None:
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self._index: faiss.IndexFlatL2 | None = None
        self._metadata: list[ChunkMetadata] = []

    @property
    def index(self) -> faiss.IndexFlatL2:
        if self._index is None:
            raise RuntimeError("FAISS index not initialized. Call create_index() or load_index().")
        return self._index

    @property
    def metadata(self) -> list[ChunkMetadata]:
        return self._metadata

    def create_index(self) -> faiss.IndexFlatL2:
        """Create a new empty FAISS IndexFlatL2."""
        logger.info("Creating FAISS IndexFlatL2 (dimension=%s)", self.dimension)
        self._index = faiss.IndexFlatL2(self.dimension)
        self._metadata = []
        logger.info("FAISS index created")
        return self._index

    def add_embeddings(
        self,
        embeddings: NDArray[np.float32],
        chunks: list[DocumentChunk] | list[ChunkMetadata] | None = None,
    ) -> int:
        """Add embedding vectors and optional chunk metadata to the index."""
        vectors = self._prepare_embeddings(embeddings)
        if chunks is not None and len(chunks) != vectors.shape[0]:
            raise ValueError(
                f"Metadata count ({len(chunks)}) must match embedding count ({vectors.shape[0]})"
            )

        self.index.add(vectors)

        if chunks is not None:
            for chunk in chunks:
                self._metadata.append(
                    {
                        "source_doc": chunk["source_doc"],
                        "chunk_text": chunk["chunk_text"],
                    }
                )

        added = vectors.shape[0]
        logger.info("Added %s embeddings to FAISS index (total=%s)", added, self.index.ntotal)
        return added

    def save_index(self) -> None:
        """Persist the FAISS index and metadata to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))

        with self.metadata_path.open("w", encoding="utf-8") as handle:
            json.dump(self._metadata, handle, ensure_ascii=False, indent=2)

        logger.info(
            "Saved FAISS index to %s (%s vectors)",
            self.index_path,
            self.index.ntotal,
        )

    def load_index(self) -> faiss.IndexFlatL2:
        """Load the FAISS index and metadata from disk."""
        if not self.index_path.is_file():
            raise FileNotFoundError(f"FAISS index not found: {self.index_path}")

        self._index = faiss.read_index(str(self.index_path))

        if self.metadata_path.is_file():
            with self.metadata_path.open(encoding="utf-8") as handle:
                self._metadata = json.load(handle)
        else:
            self._metadata = []
            logger.warning("Metadata file not found: %s", self.metadata_path)

        logger.info(
            "Loaded FAISS index from %s (%s vectors, %s metadata entries)",
            self.index_path,
            self._index.ntotal,
            len(self._metadata),
        )
        return self._index

    def search(
        self,
        query_embedding: NDArray[np.float32],
        k: int = 3,
    ) -> list[SearchResult]:
        """Search the index for the k nearest neighbors."""
        if self.index.ntotal == 0:
            raise RuntimeError("FAISS index is empty. Add embeddings before searching.")

        query = self._prepare_query(query_embedding)
        k = min(k, self.index.ntotal)

        distances, indices = self.index.search(query, k)

        results: list[SearchResult] = []
        for distance, idx in zip(distances[0], indices[0], strict=True):
            if idx < 0:
                continue

            meta = self._metadata[idx] if idx < len(self._metadata) else {
                "source_doc": "unknown",
                "chunk_text": "",
            }
            distance_value = float(distance)
            results.append(
                {
                    "source_doc": meta["source_doc"],
                    "chunk_text": meta["chunk_text"],
                    "distance": distance_value,
                    "similarity_score": self._distance_to_similarity(distance_value),
                    "index": int(idx),
                }
            )

        return results

    @staticmethod
    def _prepare_embeddings(embeddings: NDArray[np.float32]) -> NDArray[np.float32]:
        vectors = np.asarray(embeddings, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        if vectors.ndim != 2:
            raise ValueError("Embeddings must be a 1D or 2D array")
        if vectors.shape[1] != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Expected embedding dimension {EMBEDDING_DIMENSION}, got {vectors.shape[1]}"
            )
        return np.ascontiguousarray(vectors)

    def _prepare_query(self, query_embedding: NDArray[np.float32]) -> NDArray[np.float32]:
        query = self._prepare_embeddings(query_embedding)
        if query.shape[0] != 1:
            raise ValueError("Query embedding must be a single vector")
        return query

    @staticmethod
    def _distance_to_similarity(distance: float) -> float:
        # For L2-normalized vectors: ||a-b||^2 = 2 - 2*cos(theta)
        cosine_similarity = 1.0 - (distance / 2.0)
        return float(max(0.0, min(1.0, cosine_similarity)))


_default_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _default_store
    if _default_store is None:
        _default_store = VectorStore()
    return _default_store


def create_index() -> faiss.IndexFlatL2:
    return get_vector_store().create_index()


def add_embeddings(
    embeddings: NDArray[np.float32],
    chunks: list[DocumentChunk] | list[ChunkMetadata] | None = None,
) -> int:
    return get_vector_store().add_embeddings(embeddings, chunks)


def save_index() -> None:
    get_vector_store().save_index()


def load_index() -> faiss.IndexFlatL2:
    return get_vector_store().load_index()


def search(query_embedding: NDArray[np.float32], k: int = 3) -> list[SearchResult]:
    return get_vector_store().search(query_embedding, k=k)
