from __future__ import annotations

from pydantic import BaseModel, Field

from app.agents.reasoning import ReasoningStep


class AgentDryRunResponse(BaseModel):
    final_action: str
    reasoning_trace: list[ReasoningStep] = Field(default_factory=list)


class AgentExecuteResponse(BaseModel):
    final_action: str
    action_saved: bool
