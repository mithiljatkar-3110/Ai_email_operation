from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TypedDict
from uuid import UUID

from google import genai
from google.genai import types
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.contact import Contact
from app.models.email import Email
from app.rag.retriever import Retriever, RetrievedChunk, get_retriever
from app.services.exceptions import EmailNotFoundError
from app.services.thread_context_service import ThreadContextService

logger = logging.getLogger(__name__)

DRAFT_REPLY_SYSTEM = (
    "You are a professional customer support agent for FlowStack. "
    "Draft a clear, empathetic email reply using the provided context. "
    "Cite specific policies or KB excerpts when relevant. "
    "Return only the reply body text — no subject line or metadata."
)

HOLDING_REPLY_SYSTEM = (
    "You are a senior customer support agent for FlowStack. "
    "Draft an empathetic HOLDING reply acknowledging the customer's concerns. "
    "Do not admit liability or make binding legal commitments. "
    "Reference applicable SLA credit policy excerpts when provided. "
    "Confirm the matter is under senior review and legal has been notified. "
    "Return only the reply body text — no subject line or metadata."
)


class ContactNotFoundError(Exception):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Contact '{email}' not found")


class DraftReplyError(Exception):
    """Raised when Gemini cannot produce a draft reply."""


class ContactProfile(TypedDict):
    email: str
    name: str | None
    company: str | None
    status: str
    account_value: float | None
    churn_risk_score: float | None
    open_tickets: list[str]
    last_contact_at: str | None


class InternalTicket(TypedDict):
    ticket_id: str
    title: str
    body: str
    assignee: str
    status: str
    created_at: str


class EscalationResult(TypedDict):
    escalation_id: str
    email_id: str
    reason: str
    priority: int
    status: str
    brief: str
    queued_at: str


class AccountStatus(TypedDict):
    email: str
    subscription_tier: str
    billing_status: str
    renewal_status: str
    overdue_invoices: list[str]


class AgentTools:
    """Agent-callable tools for knowledge retrieval, CRM lookup, and mock actions."""

    def __init__(
        self,
        db: Session,
        *,
        thread_context_service: ThreadContextService | None = None,
        retriever: Retriever | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.db = db
        self.thread_context_service = thread_context_service or ThreadContextService(db)
        self.retriever = retriever or get_retriever()
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self._gemini_client: genai.Client | None = None

    def search_knowledge_base(self, query: str) -> list[RetrievedChunk]:
        """Search internal knowledge base via the RAG retriever."""
        logger.info("Agent tool search_knowledge_base query=%r", query[:120])
        return self.retriever.retrieve(query)

    def get_thread_history(self, thread_id: str) -> str:
        """Return chronological thread history formatted for LLM context."""
        logger.info("Agent tool get_thread_history thread_id=%s", thread_id)
        return self.thread_context_service.get_thread_context(thread_id)

    def get_contact_profile(self, email: str) -> ContactProfile:
        """Fetch CRM profile for a contact by email address."""
        logger.info("Agent tool get_contact_profile email=%s", email)
        contact = self.db.scalar(select(Contact).where(Contact.email == email))
        if contact is None:
            raise ContactNotFoundError(email)

        return ContactProfile(
            email=contact.email,
            name=contact.name,
            company=contact.company,
            status=contact.status.value,
            account_value=float(contact.account_value) if contact.account_value is not None else None,
            churn_risk_score=contact.churn_risk_score,
            open_tickets=[],
            last_contact_at=(
                contact.last_contact_at.isoformat() if contact.last_contact_at is not None else None
            ),
        )

    def create_internal_ticket(self, title: str, body: str, assignee: str) -> InternalTicket:
        """Create a mock internal support/engineering ticket (no external integration)."""
        ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
        logger.info("Agent tool create_internal_ticket ticket_id=%s assignee=%s", ticket_id, assignee)
        return InternalTicket(
            ticket_id=ticket_id,
            title=title,
            body=body,
            assignee=assignee,
            status="open",
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def check_account_status(self, email: str) -> AccountStatus:
        """Return billing tier, renewal status, and overdue invoices for a contact."""
        logger.info("Agent tool check_account_status email=%s", email)
        contact = self.db.scalar(select(Contact).where(Contact.email == email))

        if email.lower() == "bob.jones@enterprise.net":
            return AccountStatus(
                email=email,
                subscription_tier="Enterprise",
                billing_status="current",
                renewal_status="on_hold",
                overdue_invoices=[],
            )

        tier = "Enterprise" if contact and contact.status.value == "VIP" else "Standard"
        return AccountStatus(
            email=email,
            subscription_tier=tier,
            billing_status="current",
            renewal_status="active",
            overdue_invoices=[],
        )

    def flag_for_legal(
        self,
        email_id: UUID,
        *,
        issue_type: str = "legal_threat",
    ) -> dict[str, str | bool]:
        """Mark an email for legal review (MVP: in-memory flag, no separate queue table)."""
        email = self.db.get(Email, email_id)
        if email is None:
            raise EmailNotFoundError(str(email_id))

        logger.info(
            "Agent tool flag_for_legal email_id=%s issue_type=%s",
            email_id,
            issue_type,
        )
        return {
            "email_id": str(email_id),
            "flagged": True,
            "issue_type": issue_type,
            "note": "Legal flag recorded (no legal_queue table in MVP)",
        }

    def escalate_to_human(self, email_id: str, reason: str, priority: int) -> EscalationResult:
        """Queue a mock human escalation with a pre-filled brief (no external routing)."""
        try:
            email_uuid = UUID(email_id)
        except ValueError as exc:
            raise EmailNotFoundError(email_id) from exc

        email = self.db.scalar(select(Email).where(Email.id == email_uuid))
        if email is None:
            raise EmailNotFoundError(email_id)

        escalation_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
        brief = (
            f"Escalation for email {email_id}\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject or '(no subject)'}\n"
            f"Priority: {priority}\n"
            f"Reason: {reason}"
        )
        logger.info(
            "Agent tool escalate_to_human escalation_id=%s email_id=%s priority=%s",
            escalation_id,
            email_id,
            priority,
        )
        return EscalationResult(
            escalation_id=escalation_id,
            email_id=email_id,
            reason=reason,
            priority=priority,
            status="queued",
            brief=brief,
            queued_at=datetime.now(timezone.utc).isoformat(),
        )

    def draft_reply(self, context: str) -> str:
        """Generate a contextual email reply using Gemini."""
        return self._draft_with_system(context, DRAFT_REPLY_SYSTEM)

    def draft_holding_reply(self, context: str) -> str:
        """Generate an empathetic holding reply citing SLA policy (no binding commitments)."""
        return self._draft_with_system(context, HOLDING_REPLY_SYSTEM)

    def _draft_with_system(self, context: str, system_instruction: str) -> str:
        if not context.strip():
            raise DraftReplyError("Context cannot be empty")

        logger.info("Agent tool draft context_chars=%s", len(context))
        client = self._get_gemini_client()
        try:
            response = client.models.generate_content(
                model=self.model,
                contents=context.strip(),
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    max_output_tokens=settings.classification_max_output_tokens,
                ),
            )
        except Exception as exc:
            raise DraftReplyError(f"Gemini API call failed: {exc}") from exc

        text = response.text
        if not text or not text.strip():
            raise DraftReplyError("Gemini returned an empty draft reply")
        return text.strip()

    def _get_gemini_client(self) -> genai.Client:
        if not self.api_key:
            raise DraftReplyError("GEMINI_API_KEY is not configured")
        if self._gemini_client is None:
            self._gemini_client = genai.Client(api_key=self.api_key)
        return self._gemini_client
