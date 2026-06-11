from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_retriever
from app.rag.retriever import Retriever
from app.schemas.rag import RAGSearchResult

rag_router = APIRouter(prefix="/rag", tags=["rag"])


@rag_router.get(
    "/search",
    response_model=list[RAGSearchResult],
    summary="Search the knowledge base",
)
def rag_search(
    q: str = Query(..., min_length=1, description="Natural-language search query"),
    retriever: Retriever = Depends(get_retriever),
) -> list[RAGSearchResult]:
    try:
        return retriever.retrieve(q, k=3)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_QUERY",
                "message": str(exc),
                "details": {"q": q},
            },
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "RAG_INDEX_NOT_FOUND",
                "message": str(exc),
                "details": {"hint": "Run python scripts/seed_kb.py to build the index"},
            },
        ) from exc
