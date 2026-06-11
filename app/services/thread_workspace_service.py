from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.action import Action
from app.models.email import Email
from app.models.thread import Thread
from app.services.exceptions import ThreadNotFoundError


class ThreadWorkspaceService:
    """Assemble thread workspace payload for the frontend thread view."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_workspace(self, thread_id: str) -> dict[str, Any]:
        thread = self.db.scalar(select(Thread).where(Thread.thread_id == thread_id))
        if thread is None:
            raise ThreadNotFoundError(thread_id)

        emails = self.db.scalars(
            select(Email)
            .where(Email.thread_id == thread.id)
            .order_by(Email.timestamp.asc())
        ).all()

        email_ids = [email.id for email in emails]
        actions = (
            self.db.scalars(
                select(Action)
                .where(Action.email_id.in_(email_ids))
                .order_by(Action.executed_at.desc().nullslast(), Action.id.desc())
            ).all()
            if email_ids
            else []
        )

        thread_items = [_serialize_email(email) for email in emails]
        classification = _latest_classification(emails)
        agent_actions = [_serialize_action(action) for action in actions]
        reasoning_trace = _latest_reasoning_trace(actions)

        return {
            "thread": thread_items,
            "classification": classification,
            "agent_actions": agent_actions,
            "reasoning_trace": reasoning_trace,
        }


def _serialize_email(email: Email) -> dict[str, Any]:
    return {
        "email_id": str(email.id),
        "message_id": email.message_id,
        "sender": email.sender,
        "subject": email.subject or "",
        "body": email.body or "",
        "timestamp": email.timestamp.isoformat(),
        "status": email.status.value,
        "category": email.category or "",
        "urgency": email.urgency or "",
        "confidence": email.confidence,
    }


def _latest_classification(emails: list[Email]) -> dict[str, Any] | None:
    for email in reversed(emails):
        if email.category is not None and email.urgency is not None and email.confidence is not None:
            return {
                "email_id": str(email.id),
                "category": email.category,
                "urgency": email.urgency,
                "confidence": email.confidence,
                "requires_human": email.requires_human,
                "sentiment_score": email.sentiment_score,
            }
    return None


def _serialize_action(action: Action) -> dict[str, Any]:
    return {
        "action_id": str(action.id),
        "action_type": action.action_type,
        "email_id": str(action.email_id),
        "timestamp": action.executed_at.isoformat() if action.executed_at else "",
        "proposed_content": action.proposed_content,
    }


def _latest_reasoning_trace(actions: list[Action]) -> list[dict[str, str]]:
    if not actions:
        return []

    log = actions[0].agent_reasoning_log
    if not log or not isinstance(log, list):
        return []

    trace: list[dict[str, str]] = []
    for step in log:
        if not isinstance(step, dict):
            continue
        trace.append(
            {
                "thought": str(step.get("thought", "")),
                "action": str(step.get("action", "")),
                "observation": str(step.get("observation", "")),
            }
        )
    return trace
