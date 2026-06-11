from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.email import Email
from app.models.enums import EmailStatus
from app.rag.retriever import Retriever
from app.schemas.classification import ClassificationResult
from app.services.exceptions import EmailNotFoundError
from app.services.llm_classifier import LLMClassifier
from app.services.thread_context_service import ThreadContextService

logger = logging.getLogger(__name__)


class ClassificationService:
    """Orchestrate thread context, RAG retrieval, LLM classification, and persistence."""

    def __init__(
        self,
        db: Session,
        thread_context_service: ThreadContextService,
        retriever: Retriever,
        llm_classifier: LLMClassifier,
    ) -> None:
        self.db = db
        self.thread_context_service = thread_context_service
        self.retriever = retriever
        self.llm_classifier = llm_classifier

    def classify_by_email_id(self, email_id: UUID) -> ClassificationResult:
        """Classify an email without persisting results (for testing)."""
        email = self._get_email_or_raise(email_id)
        return self._classify_email(email)

    def run_classification_pipeline(self, email_id: UUID) -> ClassificationResult:
        """Classify an email and persist results to the database."""
        email = self._get_email_or_raise(email_id)
        result = self._classify_email(email)
        self._save_classification(email, result)
        logger.info(
            "Classification pipeline complete email_id=%s category=%s confidence=%.2f",
            email_id,
            result.category,
            result.confidence,
        )
        return result

    def _get_email_or_raise(self, email_id: UUID) -> Email:
        email = self.db.scalar(
            select(Email)
            .options(joinedload(Email.thread))
            .where(Email.id == email_id)
        )
        if email is None:
            raise EmailNotFoundError(str(email_id))
        return email

    def _classify_email(self, email: Email) -> ClassificationResult:
        thread_history = self.thread_context_service.get_thread_context(
            email.thread.thread_id,
            max_messages=settings.classification_max_thread_messages,
            max_body_chars=settings.classification_max_thread_body_chars,
            exclude_message_id=email.message_id,
            compact=True,
        )

        rag_query = f"{email.subject or ''} {email.body or ''}".strip()[:500]
        rag_chunks = self.retriever.retrieve(
            rag_query,
            k=settings.classification_rag_top_k,
        )

        body = email.body or ""
        if len(body) > settings.classification_max_email_body_chars:
            body = f"{body[: settings.classification_max_email_body_chars].rstrip()}..."

        return self.llm_classifier.classify(
            current_email={
                "sender": email.sender,
                "subject": email.subject or "",
                "body": body,
            },
            thread_history=thread_history,
            rag_chunks=rag_chunks,
        )

    def _save_classification(self, email: Email, result: ClassificationResult) -> None:
        preserved_status = email.status
        email.category = result.category
        email.urgency = result.urgency
        email.confidence = result.confidence
        email.requires_human = result.requires_human
        email.sentiment_score = result.sentiment_score
        if preserved_status in {EmailStatus.IGNORED, EmailStatus.ESCALATED}:
            email.status = preserved_status
        self.db.commit()
        self.db.refresh(email)
