from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import EmailStatus

if TYPE_CHECKING:
    from app.models.action import Action
    from app.models.thread import Thread


class Email(Base):
    __tablename__ = "emails"
    __table_args__ = (
        Index("ix_emails_thread_id", "thread_id"),
        Index("ix_emails_sender", "sender"),
        Index("ix_emails_timestamp", "timestamp"),
        Index("ix_emails_status", "status"),
        Index("ix_emails_sender_timestamp", "sender", "timestamp"),
        Index("ix_emails_priority_score", "priority_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
    )
    message_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    sender: Mapped[str] = mapped_column(String(320), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(32), nullable=True)
    priority_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    requires_human: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_entities: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[EmailStatus] = mapped_column(
        Enum(EmailStatus, name="email_status", native_enum=False),
        nullable=False,
        default=EmailStatus.RECEIVED,
    )

    thread: Mapped[Thread] = relationship("Thread", back_populates="emails")
    actions: Mapped[list[Action]] = relationship(
        "Action",
        back_populates="email",
        cascade="all, delete-orphan",
        order_by="Action.executed_at",
    )
