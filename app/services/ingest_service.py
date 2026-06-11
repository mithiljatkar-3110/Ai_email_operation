import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.enums import EmailStatus
from app.models.thread import Thread
from app.schemas.email import EmailIn, EmailResponse
from app.services.exceptions import DuplicateMessageError
from app.services.heuristics import triage_email

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _apply_heuristics(
        self, payload: EmailIn
    ) -> tuple[str, str | None, EmailStatus, int]:
        heuristic = triage_email(payload.sender, payload.subject, payload.body)
        logger.info(
            "Heuristic triage message_id=%s result=%s",
            payload.message_id,
            heuristic,
        )

        urgency = heuristic["urgency"]
        category: str | None = None
        status = EmailStatus.RECEIVED

        if heuristic["is_spam"]:
            category = "Spam"
            status = EmailStatus.IGNORED
        elif heuristic["is_security"]:
            urgency = "Critical"
            status = EmailStatus.ESCALATED

        return urgency, category, status, heuristic["priority_score"]

    def ingest(self, payload: EmailIn) -> EmailResponse:
        existing_email = self.db.scalar(
            select(Email).where(Email.message_id == payload.message_id)
        )
        if existing_email is not None:
            raise DuplicateMessageError(payload.message_id)

        urgency, category, status, priority_score = self._apply_heuristics(payload)

        thread = self.db.scalar(
            select(Thread).where(Thread.thread_id == payload.thread_id)
        )
        if thread is None:
            thread = Thread(
                thread_id=payload.thread_id,
                subject=payload.subject,
                sender_email=payload.sender,
                first_seen_at=payload.timestamp,
                last_updated_at=payload.timestamp,
            )
            self.db.add(thread)
            self.db.flush()
        elif payload.timestamp > thread.last_updated_at:
            thread.last_updated_at = payload.timestamp

        email = Email(
            thread_id=thread.id,
            message_id=payload.message_id,
            sender=payload.sender,
            subject=payload.subject,
            body=payload.body,
            timestamp=payload.timestamp,
            urgency=urgency,
            priority_score=priority_score,
            category=category,
            status=status,
        )
        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)

        return EmailResponse(job_id=email.id, status="accepted")
