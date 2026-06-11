from __future__ import annotations

from pathlib import Path
from typing import TypedDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

KNOWLEDGE_BASE_DOCUMENTS: tuple[str, ...] = (
    "pricing_policy.md",
    "sla_policy.md",
    "refund_policy.md",
    "api_docs.md",
    "compliance_faq.md",
    "escalation_matrix.md",
)


class LoadedDocument(TypedDict):
    source_doc: str
    content: str


def load_documents(
    knowledge_base_dir: Path | str | None = None,
) -> list[LoadedDocument]:
    """Load all enterprise knowledge base markdown files."""
    base_dir = Path(knowledge_base_dir) if knowledge_base_dir else DEFAULT_KNOWLEDGE_BASE_DIR

    if not base_dir.is_dir():
        raise FileNotFoundError(f"Knowledge base directory not found: {base_dir}")

    documents: list[LoadedDocument] = []

    for filename in KNOWLEDGE_BASE_DOCUMENTS:
        file_path = base_dir / filename
        if not file_path.is_file():
            raise FileNotFoundError(f"Required knowledge base document not found: {file_path}")

        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"Knowledge base document is empty: {filename}")

        documents.append(
            {
                "source_doc": filename,
                "content": content,
            }
        )

    return documents
