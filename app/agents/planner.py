from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agents.agent_state import AgentState
from app.agents.churn_detection import detect_churn_triggers

CONFIDENCE_THRESHOLD = 0.7

SLA_LEGAL_TRIGGERS = (
    "sla breach",
    "legal review",
    "attorney",
    "breach of contract",
)


@dataclass(frozen=True)
class PlannedStep:
    thought: str
    action: str
    is_final: bool = False
    final_action: str | None = None


class TriagePlanner:
    """Select the next ReAct step from agent state and triage rules."""

    def __init__(self, db: Session | None = None) -> None:
        self.db = db

    def resolve_workflow(self, state: AgentState) -> str:
        email = state.email
        text = f"{email.subject or ''} {email.body or ''}".lower()
        if any(trigger in text for trigger in SLA_LEGAL_TRIGGERS):
            return "bob_jones"

        if self.db is not None:
            churn_triggers = detect_churn_triggers(self.db, email)
            if churn_triggers:
                state.churn_triggers = churn_triggers
                return "churn_risk"

        if state.confidence < CONFIDENCE_THRESHOLD:
            return "immediate_escalate"
        if state.classification.get("requires_human"):
            return "immediate_escalate"
        if state.urgency == "Critical":
            return "immediate_escalate"
        if state.category == "Spam":
            return "immediate_ignore"
        if state.category == "Compliance":
            return "compliance"
        if state.category == "Legal":
            return "legal"
        if state.category == "Complaint" and state.urgency == "High":
            return "immediate_escalate"
        return "default"

    def plan(self, state: AgentState) -> PlannedStep:
        if state.workflow is None:
            state.workflow = self.resolve_workflow(state)

        planners = {
            "bob_jones": self._plan_bob_jones,
            "churn_risk": self._plan_churn_risk,
            "immediate_escalate": self._plan_immediate_escalate,
            "immediate_ignore": self._plan_immediate_ignore,
            "compliance": self._plan_compliance,
            "legal": self._plan_legal,
            "default": self._plan_default,
        }
        return planners[state.workflow](state)

    def _plan_immediate_escalate(self, state: AgentState) -> PlannedStep:
        if state.confidence < CONFIDENCE_THRESHOLD:
            reason = (
                f"Classification confidence {state.confidence:.2f} "
                f"is below {CONFIDENCE_THRESHOLD}"
            )
            thought = "Low confidence — escalate to human rather than auto-act."
        elif state.classification.get("requires_human"):
            reason = "Classification flagged requires_human=True"
            thought = "Classifier requires human review before any automated action."
        elif state.urgency == "Critical":
            reason = "Critical urgency requires human handling"
            thought = "Critical urgency emails must not receive auto-replies."
        else:
            reason = "High-urgency complaint — reputation risk per escalation matrix"
            thought = "High-urgency complaint needs human handling."

        return PlannedStep(
            thought=thought,
            action=f"escalate_to_human({state.email_id_str}, reason={reason!r})",
            is_final=True,
            final_action="escalate_to_human",
        )

    def _plan_immediate_ignore(self, state: AgentState) -> PlannedStep:
        return PlannedStep(
            thought="Spam category — no response or escalation needed.",
            action="ignore",
            is_final=True,
            final_action="ignore",
        )

    def _plan_compliance(self, state: AgentState) -> PlannedStep:
        if state.workflow_step == 0:
            return PlannedStep(
                thought="Compliance email — retrieve thread context before opening a ticket.",
                action=f"get_thread_history({state.email.thread.thread_id})",
            )
        title = f"Compliance: {state.email.subject or 'Inbound email'}"
        return PlannedStep(
            thought="Open internal compliance ticket with full thread context.",
            action=f"create_internal_ticket(title={title!r}, assignee='compliance@flowstack.io')",
            is_final=True,
            final_action="create_internal_ticket",
        )

    def _plan_legal(self, state: AgentState) -> PlannedStep:
        if state.workflow_step == 0:
            return PlannedStep(
                thought="Legal category — flag for legal review before escalation.",
                action=f"flag_for_legal({state.email_id_str})",
            )
        return PlannedStep(
            thought="Legal matter flagged — route to human agent.",
            action=f"escalate_to_human({state.email_id_str}, reason='Legal category requires human review')",
            is_final=True,
            final_action="escalate_to_human",
        )

    def _plan_default(self, state: AgentState) -> PlannedStep:
        if state.workflow_step == 0:
            return PlannedStep(
                thought="Gather thread history for contextual reply drafting.",
                action=f"get_thread_history({state.email.thread.thread_id})",
            )
        if state.workflow_step == 1:
            query = f"{state.email.subject or ''} {state.email.body or ''}".strip()
            return PlannedStep(
                thought="Search knowledge base for policies relevant to this inquiry.",
                action=f"search_knowledge_base({query[:80]!r})",
            )
        return PlannedStep(
            thought="Sufficient context gathered — draft customer reply.",
            action="draft_reply(context)",
            is_final=True,
            final_action="draft_reply",
        )

    def _plan_churn_risk(self, state: AgentState) -> PlannedStep:
        thread_id = state.email.thread.thread_id
        triggers = ", ".join(state.churn_triggers) or "churn signals"
        title = f"Churn risk: {state.email.subject or 'Inbound email'}"
        steps: list[PlannedStep] = [
            PlannedStep(
                thought=(
                    f"Churn-risk triggers detected ({triggers}) — "
                    "retrieve thread history to assess interaction pattern."
                ),
                action=f"get_thread_history({thread_id})",
            ),
            PlannedStep(
                thought="Look up refund and retention policy before engaging the customer.",
                action='search_knowledge_base("refund retention")',
            ),
            PlannedStep(
                thought="Open a retention ticket for proactive save outreach.",
                action=f"create_retention_ticket(title={title!r}, customer={state.email.sender!r})",
            ),
            PlannedStep(
                thought="Escalate to assigned account manager for high-touch retention.",
                action=(
                    f"escalate_to_account_manager({state.email_id_str}, "
                    f"customer={state.email.sender!r}, reason='churn_risk: {triggers}')"
                ),
            ),
            PlannedStep(
                thought="Draft empathetic retention response citing policy and next steps.",
                action="draft_retention_reply(context)",
                is_final=True,
                final_action="retention_draft_response",
            ),
        ]
        idx = min(state.workflow_step, len(steps) - 1)
        return steps[idx]

    def _plan_bob_jones(self, state: AgentState) -> PlannedStep:
        thread_id = state.email.thread.thread_id
        steps: list[PlannedStep] = [
            PlannedStep(
                thought="SLA/legal trigger — retrieve full thread history before acting.",
                action=f"get_thread_history({thread_id})",
            ),
            PlannedStep(
                thought="Look up SLA credit obligations and breach response policy.",
                action='search_knowledge_base("SLA")',
            ),
            PlannedStep(
                thought="Check customer billing tier and renewal status.",
                action=f"check_account_status({state.email.sender!r})",
            ),
            PlannedStep(
                thought="Legal threat detected — route to legal team with context.",
                action=(
                    f"flag_for_legal({state.email_id_str}, "
                    f"issue_type='sla_breach_and_legal_review')"
                ),
            ),
            PlannedStep(
                thought="Open internal ticket for SLA breach and legal review tracking.",
                action=(
                    "create_internal_ticket("
                    f"title='SLA/Legal escalation: {state.email.subject or 'Inbound email'}', "
                    "assignee='legal@flowstack.io')"
                ),
            ),
            PlannedStep(
                thought="Draft empathetic holding reply citing SLA policy; no binding commitments.",
                action="draft_holding_reply(context)",
            ),
            PlannedStep(
                thought="Bob Jones workflow complete — escalate with pre-filled brief.",
                action=f"escalate_to_human({state.email_id_str})",
                is_final=True,
                final_action="escalate_to_human",
            ),
        ]
        idx = min(state.workflow_step, len(steps) - 1)
        return steps[idx]

    def advance(self, state: AgentState, step: PlannedStep) -> None:
        if not step.is_final:
            state.workflow_step += 1
