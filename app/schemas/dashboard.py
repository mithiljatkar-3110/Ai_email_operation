from __future__ import annotations

from pydantic import BaseModel, Field


class AgentActivityItem(BaseModel):
    action_type: str
    email_id: str
    timestamp: str
    reason: str


class InboxItem(BaseModel):
    email_id: str
    thread_id: str
    sender: str
    subject: str
    category: str
    urgency: str
    status: str
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    timestamp: str


class DashboardStats(BaseModel):
    total_emails: int = Field(..., ge=0)
    total_threads: int = Field(..., ge=0)
    critical_cases: int = Field(..., ge=0)
    escalations: int = Field(..., ge=0)
    spam_detected: int = Field(..., ge=0)
    avg_confidence: float = Field(..., ge=0.0, le=1.0)
    open_threads: int = Field(..., ge=0)
    resolved_threads: int = Field(..., ge=0)
