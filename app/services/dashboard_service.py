from __future__ import annotations

import re

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.action import Action
from app.models.email import Email
from app.models.enums import EmailStatus, ThreadStatus
from app.models.thread import Thread


class DashboardService:
    """Top-level KPI aggregates for the mission control dashboard."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_stats(self) -> dict[str, float | int]:
        total_emails = self.db.scalar(select(func.count()).select_from(Email)) or 0
        total_threads = self.db.scalar(select(func.count()).select_from(Thread)) or 0

        critical_cases = self.db.scalar(
            select(func.count()).where(Email.urgency == "Critical")
        ) or 0

        escalate_action_ids = (
            select(Action.email_id)
            .where(Action.action_type == "escalate_to_human")
            .distinct()
        )
        escalations = self.db.scalar(
            select(func.count(func.distinct(Email.id))).where(
                or_(
                    Email.requires_human.is_(True),
                    Email.status == EmailStatus.ESCALATED,
                    Email.id.in_(escalate_action_ids),
                )
            )
        ) or 0

        spam_detected = self.db.scalar(
            select(func.count()).where(Email.category == "Spam")
        ) or 0

        avg_confidence_raw = self.db.scalar(
            select(func.avg(Email.confidence)).where(Email.confidence.isnot(None))
        )
        avg_confidence = round(float(avg_confidence_raw), 4) if avg_confidence_raw is not None else 0.0

        open_threads = self.db.scalar(
            select(func.count()).where(Thread.status == ThreadStatus.OPEN)
        ) or 0

        resolved_threads = self.db.scalar(
            select(func.count()).where(Thread.status == ThreadStatus.RESOLVED)
        ) or 0

        return {
            "total_emails": total_emails,
            "total_threads": total_threads,
            "critical_cases": critical_cases,
            "escalations": escalations,
            "spam_detected": spam_detected,
            "avg_confidence": avg_confidence,
            "open_threads": open_threads,
            "resolved_threads": resolved_threads,
        }

    def get_inbox(self, *, limit: int = 50, offset: int = 0) -> list[dict[str, str | float | None]]:
        emails = self.db.scalars(
            select(Email)
            .order_by(Email.timestamp.desc())
            .limit(limit)
            .offset(offset)
        ).all()

        return [
            {
                "email_id": str(email.id),
                "sender": email.sender,
                "subject": email.subject or "",
                "category": email.category or "",
                "urgency": email.urgency or "",
                "status": email.status.value,
                "confidence": email.confidence,
                "timestamp": email.timestamp.isoformat(),
            }
            for email in emails
        ]

    def get_agent_activity(self, *, limit: int = 50) -> list[dict[str, str]]:
        actions = self.db.scalars(
            select(Action)
            .order_by(Action.executed_at.desc().nullslast(), Action.id.desc())
            .limit(limit)
        ).all()

        return [
            {
                "action_type": action.action_type,
                "email_id": str(action.email_id),
                "timestamp": (
                    action.executed_at.isoformat()
                    if action.executed_at is not None
                    else ""
                ),
                "reason": _extract_action_reason(action),
            }
            for action in actions
        ]


_REASON_PATTERN = re.compile(r"reason=(['\"])(.+?)\1")


def _extract_action_reason(action: Action) -> str:
    log = action.agent_reasoning_log
    if not log or not isinstance(log, list):
        return _reason_from_action_type(action.action_type)

    for step in reversed(log):
        if not isinstance(step, dict):
            continue
        action_str = step.get("action", "")
        if isinstance(action_str, str):
            match = _REASON_PATTERN.search(action_str)
            if match:
                return match.group(2)
        thought = step.get("thought", "")
        if isinstance(thought, str) and thought.strip():
            return thought.strip()

    return _reason_from_action_type(action.action_type)


def _reason_from_action_type(action_type: str) -> str:
    labels = {
        "escalate_to_human": "Escalated to human agent",
        "draft_reply": "Draft reply generated",
        "retention_draft_response": "Retention reply drafted",
        "ignore": "Marked as spam/ignored",
        "create_internal_ticket": "Internal ticket created",
    }
    return labels.get(action_type, action_type.replace("_", " ").title())
