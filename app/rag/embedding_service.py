from __future__ import annotations

import logging
import threading
from typing import ClassVar

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    """Singleton wrapper around the sentence-transformers embedding model."""

    _instance: ClassVar[EmbeddingService | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls) -> EmbeddingService:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._model = None
        return cls._instance

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
                    self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
                    dimension = self._model.get_sentence_embedding_dimension()
                    logger.info(
                        "Embedding model loaded successfully (dimensions=%s)",
                        dimension,
                    )
        return self._model

    def embed_text(self, text: str) -> NDArray[np.float32]:
        if not text.strip():
            raise ValueError("Cannot embed empty text")

        model = self._get_model()
        embedding = model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(embedding, dtype=np.float32)

    def embed_documents(self, texts: list[str]) -> NDArray[np.float32]:
        if not texts:
            raise ValueError("Cannot embed an empty list of texts")

        non_empty_texts = [text for text in texts if text.strip()]
        if len(non_empty_texts) != len(texts):
            raise ValueError("Cannot embed empty text in document list")

        model = self._get_model()
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype=np.float32)


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def embed_text(text: str) -> NDArray[np.float32]:
    return get_embedding_service().embed_text(text)


def embed_documents(texts: list[str]) -> NDArray[np.float32]:
    return get_embedding_service().embed_documents(texts)
