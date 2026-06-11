from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.thread import Thread
from app.services.exceptions import ThreadNotFoundError


class ThreadContextService:
    """Build LLM-ready formatted context from a conversation thread."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_thread_context(
        self,
        thread_id: str,
        *,
        max_messages: int | None = None,
        max_body_chars: int | None = None,
        exclude_message_id: str | None = None,
        compact: bool = False,
    ) -> str:
        """Return chronological thread history as a formatted prompt string."""
        thread = self.db.scalar(select(Thread).where(Thread.thread_id == thread_id))
        if thread is None:
            raise ThreadNotFoundError(thread_id)

        emails = self.db.scalars(
            select(Email)
            .where(Email.thread_id == thread.id)
            .order_by(Email.timestamp.asc())
        ).all()

        if exclude_message_id:
            emails = [email for email in emails if email.message_id != exclude_message_id]

        if max_messages is not None and len(emails) > max_messages:
            emails = emails[-max_messages:]

        return self._format_thread_context(
            thread_id=thread.thread_id,
            emails=emails,
            max_body_chars=max_body_chars,
            compact=compact,
        )

    @staticmethod
    def _format_timestamp(value: datetime) -> str:
        if value.tzinfo is None:
            return value.isoformat()
        return value.isoformat()

    def _format_thread_context(
        self,
        thread_id: str,
        emails: list[Email],
        *,
        max_body_chars: int | None = None,
        compact: bool = False,
    ) -> str:
        if not emails:
            return f"Thread {thread_id}: (no prior messages)"

        if compact:
            lines = [f"Thread {thread_id} ({len(emails)} prior msg):"]
            for index, email in enumerate(emails, start=1):
                subject = email.subject or "(no subject)"
                body = self._truncate_text(email.body or "", max_body_chars)
                lines.append(
                    f"[{index}] {self._format_timestamp(email.timestamp)} | "
                    f"{email.sender} | {subject}\n{body}"
                )
            return "\n".join(lines)

        lines = [
            f"=== Email Thread: {thread_id} ===",
            f"Total messages: {len(emails)}",
            "",
        ]

        for index, email in enumerate(emails, start=1):
            subject = email.subject or "(no subject)"
            body = self._truncate_text(email.body or "(empty body)", max_body_chars)

            lines.extend(
                [
                    f"--- Message {index} ---",
                    f"Timestamp: {self._format_timestamp(email.timestamp)}",
                    f"From: {email.sender}",
                    f"Subject: {subject}",
                    "Body:",
                    body,
                    "",
                ]
            )

        return "\n".join(lines).rstrip()

    @staticmethod
    def _truncate_text(text: str, max_chars: int | None) -> str:
        if max_chars is None or len(text) <= max_chars:
            return text
        return f"{text[:max_chars].rstrip()}..."
