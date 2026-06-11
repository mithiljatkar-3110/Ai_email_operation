from __future__ import annotations

from sqlalchemy import Date, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models.action import Action
from app.models.email import Email
from app.models.enums import EmailStatus

CONFIDENCE_HIGH = 0.8
CONFIDENCE_MEDIUM = 0.6

ACTION_TYPE_ALIASES = {
    "create_internal_ticket": "create_ticket",
    "create_retention_ticket": "create_ticket",
    "retention_draft_response": "draft_reply",
}


class AnalyticsService:
    """Aggregate CRM metrics for dashboard charts."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def category_breakdown(self) -> dict[str, int]:
        rows = self.db.execute(
            select(Email.category, func.count())
            .where(Email.category.isnot(None))
            .group_by(Email.category)
            .order_by(func.count().desc())
        ).all()
        return {category: count for category, count in rows}

    def sentiment_trend(self) -> list[dict[str, float | str]]:
        day = cast(Email.timestamp, Date)
        rows = self.db.execute(
            select(
                day.label("date"),
                func.avg(Email.sentiment_score).label("avg_sentiment"),
            )
            .where(Email.sentiment_score.isnot(None))
            .group_by(day)
            .order_by(day)
        ).all()
        return [
            {
                "date": row.date.isoformat(),
                "avg_sentiment": round(float(row.avg_sentiment), 4),
            }
            for row in rows
        ]

    def escalation_rate(self) -> dict[str, float | int]:
        total_emails = self.db.scalar(select(func.count()).select_from(Email)) or 0

        escalate_action_ids = (
            select(Action.email_id)
            .where(Action.action_type == "escalate_to_human")
            .distinct()
        )
        escalated = self.db.scalar(
            select(func.count(func.distinct(Email.id))).where(
                or_(
                    Email.requires_human.is_(True),
                    Email.status == EmailStatus.ESCALATED,
                    Email.id.in_(escalate_action_ids),
                )
            )
        ) or 0

        rate = round((escalated / total_emails) * 100, 1) if total_emails else 0.0
        return {
            "total_emails": total_emails,
            "escalated": escalated,
            "rate": rate,
        }

    def action_distribution(self) -> dict[str, int]:
        rows = self.db.execute(
            select(Action.action_type, func.count())
            .group_by(Action.action_type)
            .order_by(func.count().desc())
        ).all()

        distribution: dict[str, int] = {}
        for action_type, count in rows:
            key = ACTION_TYPE_ALIASES.get(action_type, action_type)
            distribution[key] = distribution.get(key, 0) + count
        return distribution

    def confidence_distribution(self) -> dict[str, int]:
        high = self.db.scalar(
            select(func.count()).where(
                Email.confidence.isnot(None),
                Email.confidence >= CONFIDENCE_HIGH,
            )
        ) or 0
        medium = self.db.scalar(
            select(func.count()).where(
                Email.confidence.isnot(None),
                Email.confidence >= CONFIDENCE_MEDIUM,
                Email.confidence < CONFIDENCE_HIGH,
            )
        ) or 0
        low = self.db.scalar(
            select(func.count()).where(
                Email.confidence.isnot(None),
                Email.confidence < CONFIDENCE_MEDIUM,
            )
        ) or 0
        return {
            "high": high,
            "medium": medium,
            "low": low,
        }
