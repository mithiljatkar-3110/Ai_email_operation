from __future__ import annotations

import sys
from pathlib import Path

from app.rag.chunker import DocumentChunk, chunk_document
from app.rag.document_loader import load_documents
from app.rag.embedding_service import embed_documents
from app.rag.vector_store import DEFAULT_INDEX_PATH, DEFAULT_METADATA_PATH, VectorStore


def seed_knowledge_base(
    knowledge_base_dir: Path | str | None = None,
) -> int:
    """Load, chunk, embed, and persist the knowledge base FAISS index."""
    documents = load_documents(knowledge_base_dir)
    all_chunks: list[DocumentChunk] = []

    for document in documents:
        print(f"Loaded {document['source_doc']}")
        doc_chunks = chunk_document(document)
        print(f"Created {len(doc_chunks)} chunks\n")
        all_chunks.extend(doc_chunks)

    if not all_chunks:
        print("Error: No chunks generated from knowledge base.", file=sys.stderr)
        return 1

    chunk_texts = [chunk["chunk_text"] for chunk in all_chunks]
    embeddings = embed_documents(chunk_texts)

    store = VectorStore()
    store.create_index()
    store.add_embeddings(embeddings, all_chunks)
    store.save_index()

    print("FAISS index saved")
    print("Metadata saved")
    print(f"Index: {DEFAULT_INDEX_PATH}")
    print(f"Metadata: {DEFAULT_METADATA_PATH}")
    print(f"Total chunks indexed: {len(all_chunks)}")

    return 0


def main() -> int:
    return seed_knowledge_base()


if __name__ == "__main__":
    raise SystemExit(main())
