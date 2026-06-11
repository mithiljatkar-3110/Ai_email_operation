from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import ThreadStatus

if TYPE_CHECKING:
    from app.models.email import Email


class Thread(Base):
    __tablename__ = "threads"
    __table_args__ = (
        Index("ix_threads_sender_email", "sender_email"),
        Index("ix_threads_status", "status"),
        Index("ix_threads_last_updated_at", "last_updated_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    thread_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sender_email: Mapped[str] = mapped_column(String(320), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    status: Mapped[ThreadStatus] = mapped_column(
        Enum(ThreadStatus, name="thread_status", native_enum=False),
        nullable=False,
        default=ThreadStatus.OPEN,
    )
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)

    emails: Mapped[list[Email]] = relationship(
        "Email",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Email.timestamp",
    )
