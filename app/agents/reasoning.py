from __future__ import annotations

from pydantic import BaseModel, Field


class ReasoningStep(BaseModel):
    thought: str
    action: str
    observation: str


class AgentResult(BaseModel):
    final_action: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning_trace: list[ReasoningStep] = Field(default_factory=list)
