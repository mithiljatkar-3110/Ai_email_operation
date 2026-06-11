from pydantic import BaseModel, Field


class RAGSearchResult(BaseModel):
    source_doc: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    chunk_text: str
