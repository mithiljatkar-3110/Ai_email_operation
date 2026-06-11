from __future__ import annotations

from pydantic import BaseModel, Field


class SentimentTrendPoint(BaseModel):
    date: str
    avg_sentiment: float = Field(..., ge=-1.0, le=1.0)


class EscalationRate(BaseModel):
    total_emails: int = Field(..., ge=0)
    escalated: int = Field(..., ge=0)
    rate: float = Field(..., ge=0.0, le=100.0)


class ConfidenceDistribution(BaseModel):
    high: int = Field(..., ge=0)
    medium: int = Field(..., ge=0)
    low: int = Field(..., ge=0)
