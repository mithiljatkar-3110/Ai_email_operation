from __future__ import annotations

import logging
from uuid import UUID

from app.db.database import SessionLocal
from app.models.enums import EmailStatus
from app.rag.retriever import get_retriever
from app.services.classification_service import ClassificationService
from app.services.heuristics import triage_email
from app.services.llm_classifier import get_llm_classifier
from app.services.thread_context_service import ThreadContextService

logger = logging.getLogger(__name__)


def run_post_ingest_classification(email_id: UUID) -> None:
    """Background task: run LLM classification pipeline after email ingest."""
    db = SessionLocal()
    try:
        from app.models.email import Email

        email = db.get(Email, email_id)
        if email is None:
            logger.warning("Background classification skipped — email not found: %s", email_id)
            return

        heuristic = triage_email(
            email.sender,
            email.subject or "",
            email.body or "",
        )
        if heuristic["is_spam"] or heuristic["is_internal"]:
            logger.info(
                "Background classification skipped email_id=%s (spam=%s internal=%s)",
                email_id,
                heuristic["is_spam"],
                heuristic["is_internal"],
            )
            return

        if email.status == EmailStatus.IGNORED:
            logger.info("Background classification skipped ignored email_id=%s", email_id)
            return

        if email.status == EmailStatus.RECEIVED:
            email.status = EmailStatus.PROCESSING
            db.commit()

        service = ClassificationService(
            db=db,
            thread_context_service=ThreadContextService(db),
            retriever=get_retriever(),
            llm_classifier=get_llm_classifier(),
        )
        service.run_classification_pipeline(email_id)

        email = db.get(Email, email_id)
        if email and email.status == EmailStatus.PROCESSING:
            email.status = EmailStatus.RECEIVED
            db.commit()

        logger.info("Background classification finished email_id=%s", email_id)
    except Exception:
        logger.exception("Background classification failed email_id=%s", email_id)
        db.rollback()
    finally:
        db.close()
