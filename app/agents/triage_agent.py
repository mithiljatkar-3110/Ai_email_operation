from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.agents.reasoning import AgentResult, ReasoningStep
from app.agents.tools import AgentTools
from app.models.action import Action
from app.models.email import Email
from app.services.exceptions import EmailNotFoundError

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7
MAX_WORKFLOW_TOOL_CALLS = 6

SLA_LEGAL_TRIGGERS = (
    "sla breach",
    "legal review",
    "attorney",
    "breach of contract",
)

URGENCY_PRIORITY = {
    "Critical": 100,
    "High": 75,
    "Medium": 50,
    "Low": 25,
}


class TriageAgentError(Exception):
    """Raised when triage cannot proceed."""


class TriageAgent:
    """Rule-based triage agent that loads context and returns a structured AgentResult."""

    def __init__(self, db: Session, *, tools: AgentTools | None = None) -> None:
        self.db = db
        self.tools = tools or AgentTools(db)
        self._dry_run = False

    def run(self, email_id: UUID | str, *, dry_run: bool = False) -> AgentResult:
        self._dry_run = dry_run
        email_id_str = str(email_id)
        trace: list[ReasoningStep] = []

        email = self._load_email(email_id)
        trace.append(
            ReasoningStep(
                thought="Load the target email before applying triage rules.",
                action=f"load_email({email_id_str})",
                observation=(
                    f"sender={email.sender}, subject={email.subject or '(no subject)'}, "
                    f"status={email.status.value}"
                ),
            )
        )

        classification = self._load_classification(email)
        trace.append(
            ReasoningStep(
                thought="Classification fields drive routing decisions.",
                action=f"load_classification({email_id_str})",
                observation=(
                    f"category={classification['category']}, urgency={classification['urgency']}, "
                    f"confidence={classification['confidence']:.2f}"
                ),
            )
        )

        confidence = classification["confidence"]

        if self._matches_sla_legal_escalation(email):
            return self._bob_jones_escalation_workflow(
                email=email,
                email_id_str=email_id_str,
                trace=trace,
                confidence=confidence,
            )

        thread_history = self.tools.get_thread_history(email.thread.thread_id)
        trace.append(
            ReasoningStep(
                thought="Prior thread messages provide conversational context.",
                action=f"get_thread_history({email.thread.thread_id})",
                observation=f"Retrieved {len(thread_history)} characters of thread history.",
            )
        )
        urgency = classification["urgency"]
        category = classification["category"]

        if confidence < CONFIDENCE_THRESHOLD:
            return self._escalate(
                email=email,
                email_id_str=email_id_str,
                reason=f"Classification confidence {confidence:.2f} is below {CONFIDENCE_THRESHOLD}",
                trace=trace,
                rule="confidence < 0.7",
                confidence=confidence,
            )

        if classification.get("requires_human"):
            return self._escalate(
                email=email,
                email_id_str=email_id_str,
                reason="Classification flagged requires_human=True",
                trace=trace,
                rule="requires_human == True",
                confidence=confidence,
            )

        if urgency == "Critical":
            return self._escalate(
                email=email,
                email_id_str=email_id_str,
                reason="Critical urgency requires human handling",
                trace=trace,
                rule="urgency == Critical",
                confidence=confidence,
            )

        if category == "Spam":
            return self._ignore(
                email=email,
                trace=trace,
                rule="category == Spam",
                confidence=confidence,
            )

        if category == "Compliance":
            return self._create_ticket(
                email=email,
                thread_history=thread_history,
                trace=trace,
                rule="category == Compliance",
                confidence=confidence,
            )

        if category == "Legal":
            return self._escalate_legal(
                email=email,
                email_id_str=email_id_str,
                trace=trace,
                confidence=confidence,
            )

        if category == "Complaint" and urgency == "High":
            return self._escalate(
                email=email,
                email_id_str=email_id_str,
                reason="High-urgency complaint — reputation risk per escalation matrix",
                trace=trace,
                rule="category == Complaint and urgency == High",
                confidence=confidence,
            )

        return self._draft_reply(
            email=email,
            thread_history=thread_history,
            trace=trace,
            rule="default",
            confidence=confidence,
        )

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
    def _matches_sla_legal_escalation(email: Email) -> bool:
        text = f"{email.subject or ''} {email.body or ''}".lower()
        return any(trigger in text for trigger in SLA_LEGAL_TRIGGERS)

    def _bob_jones_escalation_workflow(
        self,
        *,
        email: Email,
        email_id_str: str,
        trace: list[ReasoningStep],
        confidence: float,
    ) -> AgentResult:
        """Mandatory SLA + legal escalation chain (max 6 tool calls, then escalate)."""
        tool_calls = 0
        thread_id = email.thread.thread_id

        trace.append(
            ReasoningStep(
                thought=(
                    "SLA/legal trigger detected — run Bob Jones escalation workflow "
                    f"(max {MAX_WORKFLOW_TOOL_CALLS} tool calls)."
                ),
                action="route_bob_jones_workflow",
                observation=f"Matched SLA/legal keywords in subject or body.",
            )
        )

        # Tool 1: get_thread_history
        trace.append(
            ReasoningStep(
                thought="Retrieve full thread history before acting on legal/SLA escalation.",
                action=f"get_thread_history({thread_id})",
                observation="",
            )
        )
        thread_history = self.tools.get_thread_history(thread_id)
        tool_calls += 1
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=f"Retrieved {len(thread_history)} characters across thread {thread_id}.",
        )

        # Tool 2: search_knowledge_base("SLA")
        trace.append(
            ReasoningStep(
                thought="Look up SLA credit obligations and breach response policy.",
                action='search_knowledge_base("SLA")',
                observation="",
            )
        )
        rag_chunks = self.tools.search_knowledge_base("SLA")
        tool_calls += 1
        rag_text = "\n".join(
            f"- {chunk['source_doc']}: {chunk['chunk_text'][:350]}" for chunk in rag_chunks
        )
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=f"Retrieved {len(rag_chunks)} SLA policy chunk(s).",
        )

        # Tool 3: check_account_status
        trace.append(
            ReasoningStep(
                thought="Check customer billing tier and renewal status before escalation.",
                action=f"check_account_status({email.sender!r})",
                observation="",
            )
        )
        account = self.tools.check_account_status(email.sender)
        tool_calls += 1
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=(
                f"tier={account['subscription_tier']}, billing={account['billing_status']}, "
                f"renewal={account['renewal_status']}, overdue={len(account['overdue_invoices'])}"
            ),
        )

        # Tool 4: flag_for_legal
        issue_type = "sla_breach_and_legal_review"
        trace.append(
            ReasoningStep(
                thought="Legal threat detected — route to legal team with context.",
                action=f"flag_for_legal({email_id_str}, issue_type={issue_type!r})",
                observation="",
            )
        )
        if not self._dry_run:
            legal_flag = self.tools.flag_for_legal(email.id, issue_type=issue_type)
            flag_observation = f"Legal flag recorded: {legal_flag['issue_type']}"
        else:
            flag_observation = f"Dry-run: would flag for legal ({issue_type})."
        tool_calls += 1
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=flag_observation,
        )

        # Tool 5: create_internal_ticket
        ticket_title = f"SLA/Legal escalation: {email.subject or 'Inbound email'}"
        ticket_body = (
            f"From: {email.sender}\n"
            f"Subject: {email.subject or '(no subject)'}\n"
            f"Account tier: {account['subscription_tier']}\n"
            f"Renewal status: {account['renewal_status']}\n\n"
            f"{email.body or '(empty body)'}\n\n"
            f"--- Thread context ---\n{thread_history}\n\n"
            f"--- SLA policy excerpts ---\n{rag_text or '(none)'}"
        )
        ticket_assignee = "legal@flowstack.io"
        trace.append(
            ReasoningStep(
                thought="Open internal ticket for SLA breach and legal review tracking.",
                action=f"create_internal_ticket(title={ticket_title!r}, assignee={ticket_assignee!r})",
                observation="",
            )
        )
        ticket_id = "DRY-RUN"
        if not self._dry_run:
            ticket = self.tools.create_internal_ticket(ticket_title, ticket_body, ticket_assignee)
            ticket_id = ticket["ticket_id"]
            ticket_observation = f"Ticket created: {ticket_id}"
        else:
            ticket_observation = f"Dry-run: would create ticket '{ticket_title}' -> {ticket_assignee}"
        tool_calls += 1
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=ticket_observation,
        )

        # Tool 6: draft_holding_reply
        holding_context = (
            f"Thread history:\n{thread_history}\n\n"
            f"SLA policy excerpts:\n{rag_text or '(none)'}\n\n"
            f"Account status:\n"
            f"- Tier: {account['subscription_tier']}\n"
            f"- Billing: {account['billing_status']}\n"
            f"- Renewal: {account['renewal_status']}\n\n"
            "Current email:\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject or '(no subject)'}\n"
            f"Body: {email.body or '(empty body)'}"
        )
        trace.append(
            ReasoningStep(
                thought="Draft empathetic holding reply citing SLA policy; no binding commitments.",
                action="draft_holding_reply(context)",
                observation="",
            )
        )
        holding_reply: str | None = None
        if not self._dry_run:
            holding_reply = self.tools.draft_holding_reply(holding_context)
            draft_observation = f"Holding reply drafted ({len(holding_reply)} characters)."
        else:
            draft_observation = (
                "Dry-run: would draft holding reply citing SLA policy and account context."
            )
        tool_calls += 1
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=draft_observation,
        )

        if tool_calls > MAX_WORKFLOW_TOOL_CALLS:
            logger.warning(
                "Bob Jones workflow exceeded %s tool calls (%s)",
                MAX_WORKFLOW_TOOL_CALLS,
                tool_calls,
            )

        reason = (
            "SLA breach + legal review escalation. "
            f"Account {account['subscription_tier']} (renewal {account['renewal_status']}). "
            f"Internal ticket {ticket_id}. Legal flagged."
        )
        return self._escalate(
            email=email,
            email_id_str=email_id_str,
            reason=reason,
            trace=trace,
            rule="bob_jones_sla_legal_workflow",
            confidence=confidence,
            proposed_content_override=holding_reply,
        )

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

    def _complete(
        self,
        email: Email,
        result: AgentResult,
        *,
        proposed_content: str | None = None,
    ) -> AgentResult:
        if not self._dry_run:
            self._save_action(email, result, proposed_content=proposed_content)
        return result

    def _escalate_legal(
        self,
        *,
        email: Email,
        email_id_str: str,
        trace: list[ReasoningStep],
        confidence: float,
    ) -> AgentResult:
        trace.append(
            ReasoningStep(
                thought="Rule matched: category == Legal. Flag for legal review before escalation.",
                action=f"flag_for_legal({email_id_str})",
                observation=(
                    f"Dry-run: would flag email {email_id_str} for legal."
                    if self._dry_run
                    else f"Legal flag recorded for email {email_id_str}."
                ),
            )
        )
        if not self._dry_run:
            self.tools.flag_for_legal(email.id)

        return self._escalate(
            email=email,
            email_id_str=email_id_str,
            reason="Legal category requires human review",
            trace=trace,
            rule="category == Legal",
            confidence=confidence,
        )

    def _escalate(
        self,
        *,
        email: Email,
        email_id_str: str,
        reason: str,
        trace: list[ReasoningStep],
        rule: str,
        confidence: float,
        proposed_content_override: str | None = None,
    ) -> AgentResult:
        priority = max(email.priority_score, URGENCY_PRIORITY.get(email.urgency or "", 50))
        trace.append(
            ReasoningStep(
                thought=f"Rule matched: {rule}. Route to a human agent.",
                action=f"escalate_to_human({email_id_str}, reason={reason!r}, priority={priority})",
                observation="",
            )
        )
        proposed_content: str | None = proposed_content_override
        if self._dry_run:
            observation = f"Dry-run: would escalate with priority {priority}"
        else:
            escalation = self.tools.escalate_to_human(email_id_str, reason, priority)
            observation = f"Escalation queued: {escalation['escalation_id']}"
            if proposed_content is None:
                proposed_content = escalation["brief"]
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=observation,
        )
        logger.info("Triage escalate email_id=%s rule=%s dry_run=%s", email_id_str, rule, self._dry_run)
        return self._complete(
            email,
            AgentResult(
                final_action="escalate_to_human",
                confidence=confidence,
                reasoning_trace=trace,
            ),
            proposed_content=proposed_content,
        )

    def _ignore(
        self,
        *,
        email: Email,
        trace: list[ReasoningStep],
        rule: str,
        confidence: float,
    ) -> AgentResult:
        observation = (
            f"Dry-run: would ignore email {email.id}."
            if self._dry_run
            else f"Email {email.id} marked for ignore."
        )
        trace.append(
            ReasoningStep(
                thought=f"Rule matched: {rule}. No response or escalation needed.",
                action="ignore",
                observation=observation,
            )
        )
        logger.info("Triage ignore email_id=%s rule=%s dry_run=%s", email.id, rule, self._dry_run)
        return self._complete(
            email,
            AgentResult(
                final_action="ignore",
                confidence=confidence,
                reasoning_trace=trace,
            ),
        )

    def _create_ticket(
        self,
        *,
        email: Email,
        thread_history: str,
        trace: list[ReasoningStep],
        rule: str,
        confidence: float,
    ) -> AgentResult:
        title = f"Compliance: {email.subject or 'Inbound email'}"
        body = (
            f"From: {email.sender}\n"
            f"Subject: {email.subject or '(no subject)'}\n\n"
            f"{email.body or '(empty body)'}\n\n"
            f"--- Thread context ---\n{thread_history}"
        )
        assignee = "compliance@flowstack.io"
        trace.append(
            ReasoningStep(
                thought=f"Rule matched: {rule}. Open an internal compliance ticket.",
                action=f"create_internal_ticket(title={title!r}, assignee={assignee!r})",
                observation="",
            )
        )
        if self._dry_run:
            observation = f"Dry-run: would create ticket '{title}' assigned to {assignee}"
            proposed_content = None
        else:
            ticket = self.tools.create_internal_ticket(title, body, assignee)
            observation = f"Ticket created: {ticket['ticket_id']}"
            proposed_content = body
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=observation,
        )
        logger.info("Triage create_ticket email_id=%s rule=%s dry_run=%s", email.id, rule, self._dry_run)
        return self._complete(
            email,
            AgentResult(
                final_action="create_internal_ticket",
                confidence=confidence,
                reasoning_trace=trace,
            ),
            proposed_content=proposed_content,
        )

    def _draft_reply(
        self,
        *,
        email: Email,
        thread_history: str,
        trace: list[ReasoningStep],
        rule: str,
        confidence: float,
    ) -> AgentResult:
        rag_query = f"{email.subject or ''} {email.body or ''}".strip()
        trace.append(
            ReasoningStep(
                thought=f"Rule matched: {rule}. Retrieve policy context before drafting.",
                action=f"search_knowledge_base({rag_query[:80]!r})",
                observation="",
            )
        )
        rag_chunks = self.tools.search_knowledge_base(rag_query)
        rag_text = "\n".join(
            f"- {chunk['source_doc']}: {chunk['chunk_text'][:350]}" for chunk in rag_chunks
        )
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=f"Retrieved {len(rag_chunks)} knowledge base chunk(s).",
        )

        context = (
            f"Thread history:\n{thread_history}\n\n"
            f"Knowledge base:\n{rag_text or '(none)'}\n\n"
            "Current email:\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject or '(no subject)'}\n"
            f"Body: {email.body or '(empty body)'}"
        )
        trace.append(
            ReasoningStep(
                thought="Sufficient context gathered; generate a customer reply.",
                action="draft_reply(context)",
                observation="",
            )
        )
        if self._dry_run:
            observation = (
                f"Dry-run: would draft reply using {len(rag_chunks)} KB chunk(s) "
                f"and {len(thread_history)} characters of thread context."
            )
            proposed_content = None
        else:
            draft = self.tools.draft_reply(context)
            observation = f"Draft reply generated ({len(draft)} characters)."
            proposed_content = draft
        trace[-1] = ReasoningStep(
            thought=trace[-1].thought,
            action=trace[-1].action,
            observation=observation,
        )
        logger.info("Triage draft_reply email_id=%s rule=%s dry_run=%s", email.id, rule, self._dry_run)
        return self._complete(
            email,
            AgentResult(
                final_action="draft_reply",
                confidence=confidence,
                reasoning_trace=trace,
            ),
            proposed_content=proposed_content,
        )
