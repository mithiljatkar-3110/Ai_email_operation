from __future__ import annotations

from typing import TypedDict

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.document_loader import LoadedDocument

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


class DocumentChunk(TypedDict):
    source_doc: str
    chunk_text: str


_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
)


def chunk_document(document: LoadedDocument) -> list[DocumentChunk]:
    """Split a single loaded document into overlapping text chunks."""
    source_doc = document["source_doc"]
    content = document["content"]

    if not content.strip():
        raise ValueError(f"Document has no content to chunk: {source_doc}")

    chunks = _splitter.split_text(content)

    return [
        {
            "source_doc": source_doc,
            "chunk_text": chunk.strip(),
        }
        for chunk in chunks
        if chunk.strip()
    ]


def chunk_documents(documents: list[LoadedDocument]) -> list[DocumentChunk]:
    """Split multiple loaded documents into chunks."""
    all_chunks: list[DocumentChunk] = []
    for document in documents:
        all_chunks.extend(chunk_document(document))
    return all_chunks
