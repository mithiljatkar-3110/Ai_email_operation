from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.tools import AccountStatus
from app.models.email import Email
from app.rag.retriever import RetrievedChunk


@dataclass
class AgentState:
    email: Email
    email_id_str: str
    classification: dict[str, Any]
    dry_run: bool

    workflow: str | None = None
    workflow_step: int = 0
    tool_calls: int = 0

    thread_history: str | None = None
    rag_chunks: list[RetrievedChunk] = field(default_factory=list)
    rag_text: str = ""
    account: AccountStatus | None = None
    ticket_id: str | None = None
    ticket_body: str | None = None
    holding_reply: str | None = None
    draft_reply_text: str | None = None
    retention_reply_text: str | None = None
    legal_flagged: bool = False
    churn_triggers: list[str] = field(default_factory=list)
    account_manager_escalation_id: str | None = None

    @property
    def confidence(self) -> float:
        return float(self.classification["confidence"])

    @property
    def category(self) -> str:
        return str(self.classification["category"])

    @property
    def urgency(self) -> str:
        return str(self.classification["urgency"])
