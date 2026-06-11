from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.agents.agent_state import AgentState
from app.agents.reasoning import AgentResult, ReasoningStep
from app.agents.planner import TriagePlanner
from app.agents.react_loop import ReActLoop
from app.agents.tools import AgentTools
from app.models.action import Action
from app.models.email import Email
from app.services.exceptions import EmailNotFoundError

logger = logging.getLogger(__name__)


class TriageAgentError(Exception):
    """Raised when triage cannot proceed."""


class TriageAgent:
    """ReAct-style triage agent: Thought -> Action -> Observation until a final action."""

    def __init__(self, db: Session, *, tools: AgentTools | None = None) -> None:
        self.db = db
        self.tools = tools or AgentTools(db)

    def run(self, email_id: UUID | str, *, dry_run: bool = False) -> AgentResult:
        email_id_str = str(email_id)
        email = self._load_email(email_id)
        classification = self._load_classification(email)

        setup_trace = [
            ReasoningStep(
                thought="Load the target email before starting the ReAct loop.",
                action=f"load_email({email_id_str})",
                observation=(
                    f"sender={email.sender}, subject={email.subject or '(no subject)'}, "
                    f"status={email.status.value}"
                ),
            ),
            ReasoningStep(
                thought="Classification fields drive planner routing decisions.",
                action=f"load_classification({email_id_str})",
                observation=(
                    f"category={classification['category']}, urgency={classification['urgency']}, "
                    f"confidence={classification['confidence']:.2f}, "
                    f"requires_human={classification.get('requires_human')}"
                ),
            ),
        ]

        state = AgentState(
            email=email,
            email_id_str=email_id_str,
            classification=classification,
            dry_run=dry_run,
        )
        loop = ReActLoop(
            self.tools,
            planner=TriagePlanner(self.db),
            dry_run=dry_run,
        )
        result, proposed_content = loop.run(state)

        full_result = AgentResult(
            final_action=result.final_action,
            confidence=result.confidence,
            reasoning_trace=setup_trace + result.reasoning_trace,
        )

        if not dry_run:
            self._save_action(email, full_result, proposed_content=proposed_content)

        logger.info(
            "Triage complete email_id=%s final_action=%s steps=%s dry_run=%s",
            email_id_str,
            full_result.final_action,
            len(full_result.reasoning_trace),
            dry_run,
        )
        return full_result

    def _load_email(self, email_id: UUID | str) -> Email:
        try:
            email_uuid = email_id if isinstance(email_id, UUID) else UUID(str(email_id))
        except ValueError as exc:
            raise EmailNotFoundError(str(email_id)) from exc

        email = self.db.scalar(
            select(Email)
            .options(joinedload(Email.thread))
            .where(Email.id == email_uuid)
        )
        if email is None:
            raise EmailNotFoundError(str(email_id))
        return email

    @staticmethod
    def _load_classification(email: Email) -> dict[str, Any]:
        if email.category is None or email.urgency is None or email.confidence is None:
            raise TriageAgentError(f"Email {email.id} has not been classified yet")

        return {
            "category": email.category,
            "urgency": email.urgency,
            "confidence": email.confidence,
            "requires_human": email.requires_human,
            "sentiment_score": email.sentiment_score,
        }

    def _save_action(
        self,
        email: Email,
        result: AgentResult,
        *,
        proposed_content: str | None = None,
    ) -> Action:
        action = Action(
            email_id=email.id,
            action_type=result.final_action,
            agent_reasoning_log=[
                {
                    "thought": step.thought,
                    "action": step.action,
                    "observation": step.observation,
                }
                for step in result.reasoning_trace
            ],
            proposed_content=proposed_content,
            executed_at=datetime.now(timezone.utc),
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        logger.info(
            "Saved agent action id=%s type=%s email_id=%s",
            action.id,
            action.action_type,
            email.id,
        )
        return action
