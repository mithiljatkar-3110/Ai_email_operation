from fastapi import HTTPException, status

from app.agents.triage_agent import TriageAgentError
from app.agents.tools import ContactNotFoundError, DraftReplyError
from app.services.exceptions import EmailNotFoundError, ThreadNotFoundError


def raise_agent_http_error(exc: Exception) -> None:
    if isinstance(exc, EmailNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "EMAIL_NOT_FOUND",
                "message": str(exc),
                "details": {"email_id": exc.email_id},
            },
        ) from exc
    if isinstance(exc, ThreadNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "THREAD_NOT_FOUND",
                "message": str(exc),
                "details": {"thread_id": exc.thread_id},
            },
        ) from exc
    if isinstance(exc, TriageAgentError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "TRIAGE_NOT_READY",
                "message": str(exc),
                "details": {},
            },
        ) from exc
    if isinstance(exc, DraftReplyError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error_code": "DRAFT_REPLY_FAILED",
                "message": str(exc),
                "details": {},
            },
        ) from exc
    if isinstance(exc, ContactNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "CONTACT_NOT_FOUND",
                "message": str(exc),
                "details": {"email": exc.email},
            },
        ) from exc
    if isinstance(exc, FileNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "RAG_INDEX_NOT_FOUND",
                "message": str(exc),
                "details": {"hint": "Run python scripts/seed_kb.py"},
            },
        ) from exc
    raise exc
