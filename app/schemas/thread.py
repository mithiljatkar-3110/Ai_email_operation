from __future__ import annotations

from pydantic import BaseModel, Field

from app.agents.reasoning import ReasoningStep


class ThreadEmailItem(BaseModel):
    email_id: str
    message_id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    status: str
    category: str
    urgency: str
    confidence: float | None = Field(None, ge=0.0, le=1.0)


class ThreadClassification(BaseModel):
    email_id: str
    category: str
    urgency: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_human: bool | None = None
    sentiment_score: float | None = Field(None, ge=-1.0, le=1.0)


class ThreadAgentAction(BaseModel):
    action_id: str
    action_type: str
    email_id: str
    timestamp: str
    proposed_content: str | None = None


class ThreadWorkspaceResponse(BaseModel):
    thread: list[ThreadEmailItem] = Field(default_factory=list)
    classification: ThreadClassification | None = None
    agent_actions: list[ThreadAgentAction] = Field(default_factory=list)
    reasoning_trace: list[ReasoningStep] = Field(default_factory=list)
