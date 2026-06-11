from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

EmailCategory = Literal[
    "Complaint",
    "Inquiry",
    "Bug Report",
    "Feature Request",
    "Compliance",
    "Legal",
    "Billing",
    "Spam",
    "Internal",
    "Other",
]

SentimentLabel = Literal["Positive", "Neutral", "Negative", "Mixed"]

ClassificationUrgency = Literal["Critical", "High", "Medium", "Low"]


class DetectedEntities(BaseModel):
    order_ids: list[str] = Field(default_factory=list)
    ticket_ids: list[str] = Field(default_factory=list)
    monetary_amounts: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    products_mentioned: list[str] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    category: EmailCategory
    sentiment: SentimentLabel
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    urgency: ClassificationUrgency
    requires_human: bool
    escalation_reason: str | None = None
    suggested_reply: str | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    detected_entities: DetectedEntities = Field(default_factory=DetectedEntities)

    @model_validator(mode="after")
    def validate_human_reply_fields(self) -> ClassificationResult:
        if self.requires_human:
            if not self.escalation_reason or not self.escalation_reason.strip():
                raise ValueError("escalation_reason is required when requires_human is true")
            if self.suggested_reply is not None:
                raise ValueError("suggested_reply must be null when requires_human is true")
        else:
            if not self.suggested_reply or not self.suggested_reply.strip():
                raise ValueError("suggested_reply is required when requires_human is false")
            if self.escalation_reason is not None:
                raise ValueError("escalation_reason must be null when requires_human is false")
        return self
