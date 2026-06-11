from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.email import Email

REFUND_DEMAND_TRIGGERS = (
    "refund",
    "money back",
    "full refund",
)

REVIEW_THREAT_TRIGGERS = (
    "public review",
    "negative review",
    "leave a review",
    "leaving detailed negative",
    "post on twitter",
    "trustpilot",
    "capterra",
    "g2,",
    "g2 ",
    "on g2",
)

CANCELLATION_TRIGGERS = (
    "cancel my",
    "cancellation",
    "cancelling my",
    "canceling my",
    "delete my account",
    "unsubscribe",
)

NEGATIVE_INTERACTION_KEYWORDS = (
    "unhappy",
    "unacceptable",
    "disappointed",
    "angry",
    "warning",
    "terrible",
    "awful",
    "frustrated",
    "no reply",
    "zero human",
    "still no reply",
    "extremely unhappy",
)

NEGATIVE_SENTIMENT_THRESHOLD = -0.15
CONSECUTIVE_NEGATIVE_REQUIRED = 3


def _email_text(email: Email) -> str:
    return f"{email.subject or ''} {email.body or ''}".lower()


def _matches_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def is_negative_interaction(email: Email) -> bool:
    if email.sentiment_score is not None:
        return email.sentiment_score < NEGATIVE_SENTIMENT_THRESHOLD
    return _matches_any(_email_text(email), NEGATIVE_INTERACTION_KEYWORDS)


def count_consecutive_negative_interactions(db: Session, email: Email) -> int:
    """Count consecutive negative inbound emails from the same sender ending at `email`."""
    thread_emails = db.scalars(
        select(Email)
        .where(
            Email.thread_id == email.thread_id,
            Email.sender == email.sender,
        )
        .order_by(Email.timestamp.asc())
    ).all()

    streak = 0
    for msg in reversed(thread_emails):
        if msg.timestamp > email.timestamp:
            continue
        if is_negative_interaction(msg):
            streak += 1
        else:
            break
    return streak


def detect_churn_triggers(db: Session, email: Email) -> list[str]:
    """Return matched churn-risk trigger labels (empty if none)."""
    text = _email_text(email)
    triggers: list[str] = []

    if _matches_any(text, REFUND_DEMAND_TRIGGERS):
        triggers.append("refund_demand")

    if _matches_any(text, REVIEW_THREAT_TRIGGERS):
        triggers.append("review_threat")

    if _matches_any(text, CANCELLATION_TRIGGERS):
        triggers.append("cancellation_request")

    negative_streak = count_consecutive_negative_interactions(db, email)
    if negative_streak >= CONSECUTIVE_NEGATIVE_REQUIRED:
        triggers.append("three_consecutive_negative_interactions")

    return triggers
