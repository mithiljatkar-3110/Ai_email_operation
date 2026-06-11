from __future__ import annotations

import logging

from app.agents.agent_state import AgentState
from app.agents.planner import PlannedStep, TriagePlanner
from app.agents.reasoning import AgentResult, ReasoningStep
from app.agents.tools import AgentTools

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS = 6

URGENCY_PRIORITY = {
    "Critical": 100,
    "High": 75,
    "Medium": 50,
    "Low": 25,
}


class ReActLoop:
    """Thought -> Action -> Observation loop with a maximum tool-call budget."""

    def __init__(
        self,
        tools: AgentTools,
        *,
        planner: TriagePlanner | None = None,
        dry_run: bool = False,
    ) -> None:
        self.tools = tools
        self.planner = planner or TriagePlanner()
        self.dry_run = dry_run

    def run(self, state: AgentState) -> tuple[AgentResult, str | None]:
        trace: list[ReasoningStep] = []
        proposed_content: str | None = None

        while True:
            step = self.planner.plan(state)
            if step.is_final:
                observation, proposed_content = self._execute_final(state, step)
                trace.append(
                    ReasoningStep(
                        thought=step.thought,
                        action=step.action,
                        observation=observation,
                    )
                )
                return (
                    AgentResult(
                        final_action=step.final_action or step.action,
                        confidence=state.confidence,
                        reasoning_trace=trace,
                    ),
                    proposed_content,
                )

            if state.tool_calls >= MAX_TOOL_CALLS:
                break

            observation = self._execute_tool(state, step)
            state.tool_calls += 1
            trace.append(
                ReasoningStep(
                    thought=step.thought,
                    action=step.action,
                    observation=observation,
                )
            )
            self.planner.advance(state, step)

        reason = (
            f"Maximum {MAX_TOOL_CALLS} tool calls reached without resolution — escalating."
        )
        priority = max(
            state.email.priority_score,
            URGENCY_PRIORITY.get(state.email.urgency or "", 50),
        )
        escalation_step = PlannedStep(
            thought="Tool budget exhausted — escalate to human with reasoning summary.",
            action=f"escalate_to_human({state.email_id_str}, reason={reason!r}, priority={priority})",
            is_final=True,
            final_action="escalate_to_human",
        )
        observation, proposed_content = self._execute_final(state, escalation_step)
        trace.append(
            ReasoningStep(
                thought=escalation_step.thought,
                action=escalation_step.action,
                observation=observation,
            )
        )
        return (
            AgentResult(
                final_action="escalate_to_human",
                confidence=state.confidence,
                reasoning_trace=trace,
            ),
            proposed_content,
        )

    def _execute_tool(self, state: AgentState, step: PlannedStep) -> str:
        action = step.action
        email = state.email

        if action.startswith("get_thread_history"):
            thread_history = self.tools.get_thread_history(email.thread.thread_id)
            state.thread_history = thread_history
            return f"Retrieved {len(thread_history)} characters across thread {email.thread.thread_id}."

        if action.startswith("search_knowledge_base"):
            if '"SLA"' in action:
                query = "SLA"
            elif '"refund retention"' in action:
                query = "refund retention"
            else:
                query = f"{email.subject or ''} {email.body or ''}".strip()
            chunks = self.tools.search_knowledge_base(query)
            state.rag_chunks = chunks
            state.rag_text = "\n".join(
                f"- {c['source_doc']}: {c['chunk_text'][:350]}" for c in chunks
            )
            if query == "SLA":
                label = "SLA policy"
            elif query == "refund retention":
                label = "retention policy"
            else:
                label = "knowledge base"
            return f"Retrieved {len(chunks)} {label} chunk(s)."

        if action.startswith("check_account_status"):
            account = self.tools.check_account_status(email.sender)
            state.account = account
            return (
                f"tier={account['subscription_tier']}, billing={account['billing_status']}, "
                f"renewal={account['renewal_status']}, overdue={len(account['overdue_invoices'])}"
            )

        if action.startswith("flag_for_legal"):
            issue_type = "sla_breach_and_legal_review" if "sla_breach" in action else "legal_threat"
            if self.dry_run:
                state.legal_flagged = True
                return f"Dry-run: would flag for legal ({issue_type})."
            result = self.tools.flag_for_legal(email.id, issue_type=issue_type)
            state.legal_flagged = True
            return f"Legal flag recorded: {result['issue_type']}"

        if action.startswith("create_internal_ticket"):
            return self._create_ticket(state)

        if action.startswith("create_retention_ticket"):
            return self._create_retention_ticket(state)

        if action.startswith("escalate_to_account_manager"):
            return self._escalate_to_account_manager(state, action)

        if action == "draft_holding_reply(context)":
            return self._draft_holding(state)

        raise ValueError(f"Unknown tool action: {action}")

    def _create_ticket(self, state: AgentState) -> str:
        email = state.email
        thread_history = state.thread_history or ""

        if state.workflow == "bob_jones":
            title = f"SLA/Legal escalation: {email.subject or 'Inbound email'}"
            body = (
                f"From: {email.sender}\n"
                f"Subject: {email.subject or '(no subject)'}\n"
                f"Account tier: {state.account['subscription_tier'] if state.account else 'unknown'}\n"
                f"Renewal status: {state.account['renewal_status'] if state.account else 'unknown'}\n\n"
                f"{email.body or '(empty body)'}\n\n"
                f"--- Thread context ---\n{thread_history}\n\n"
                f"--- SLA policy excerpts ---\n{state.rag_text or '(none)'}"
            )
            assignee = "legal@flowstack.io"
        else:
            title = f"Compliance: {email.subject or 'Inbound email'}"
            body = (
                f"From: {email.sender}\n"
                f"Subject: {email.subject or '(no subject)'}\n\n"
                f"{email.body or '(empty body)'}\n\n"
                f"--- Thread context ---\n{thread_history}"
            )
            assignee = "compliance@flowstack.io"

        state.ticket_body = body
        if self.dry_run:
            state.ticket_id = "DRY-RUN"
            return f"Dry-run: would create ticket '{title}' -> {assignee}"

        ticket = self.tools.create_internal_ticket(title, body, assignee)
        state.ticket_id = ticket["ticket_id"]
        return f"Ticket created: {ticket['ticket_id']}"

    def _create_retention_ticket(self, state: AgentState) -> str:
        email = state.email
        thread_history = state.thread_history or ""
        triggers = ", ".join(state.churn_triggers) or "churn risk"
        title = f"Churn risk: {email.subject or 'Inbound email'}"
        body = (
            f"Customer: {email.sender}\n"
            f"Triggers: {triggers}\n"
            f"Subject: {email.subject or '(no subject)'}\n\n"
            f"{email.body or '(empty body)'}\n\n"
            f"--- Thread context ---\n{thread_history}\n\n"
            f"--- Retention policy excerpts ---\n{state.rag_text or '(none)'}"
        )
        state.ticket_body = body
        if self.dry_run:
            state.ticket_id = "DRY-RUN"
            return f"Dry-run: would create retention ticket '{title}' -> retention@flowstack.io"
        ticket = self.tools.create_retention_ticket(title, body, email.sender)
        state.ticket_id = ticket["ticket_id"]
        return f"Retention ticket created: {ticket['ticket_id']}"

    def _escalate_to_account_manager(self, state: AgentState, action: str) -> str:
        email = state.email
        reason = "Churn-risk customer requires account manager intervention"
        if "reason=" in action:
            start = action.index("reason=") + len("reason=")
            fragment = action[start:]
            if fragment.startswith(("'", '"')):
                quote = fragment[0]
                end = fragment.index(quote, 1)
                reason = fragment[1:end]

        priority = max(
            email.priority_score,
            URGENCY_PRIORITY.get(email.urgency or "", 75),
        )
        if self.dry_run:
            manager = self.tools._resolve_account_manager(email.sender)
            state.account_manager_escalation_id = "DRY-RUN"
            return (
                f"Dry-run: would escalate to account manager {manager} "
                f"(priority {priority})."
            )

        result = self.tools.escalate_to_account_manager(
            state.email_id_str,
            reason,
            email.sender,
            priority=priority,
        )
        state.account_manager_escalation_id = result["escalation_id"]
        return (
            f"Account manager escalation queued: {result['escalation_id']} "
            f"-> {result['account_manager']}"
        )

    def _draft_holding(self, state: AgentState) -> str:
        email = state.email
        context = (
            f"Thread history:\n{state.thread_history or ''}\n\n"
            f"SLA policy excerpts:\n{state.rag_text or '(none)'}\n\n"
            f"Account status:\n"
            f"- Tier: {state.account['subscription_tier'] if state.account else 'unknown'}\n"
            f"- Billing: {state.account['billing_status'] if state.account else 'unknown'}\n"
            f"- Renewal: {state.account['renewal_status'] if state.account else 'unknown'}\n\n"
            "Current email:\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject or '(no subject)'}\n"
            f"Body: {email.body or '(empty body)'}"
        )
        if self.dry_run:
            return "Dry-run: would draft holding reply citing SLA policy and account context."
        draft = self.tools.draft_holding_reply(context)
        state.holding_reply = draft
        return f"Holding reply drafted ({len(draft)} characters)."

    def _draft_retention(self, state: AgentState) -> tuple[str, str | None]:
        email = state.email
        triggers = ", ".join(state.churn_triggers) or "churn risk"
        context = (
            f"Churn triggers: {triggers}\n\n"
            f"Thread history:\n{state.thread_history or ''}\n\n"
            f"Retention policy excerpts:\n{state.rag_text or '(none)'}\n\n"
            f"Retention ticket: {state.ticket_id or 'pending'}\n"
            f"Account manager escalation: {state.account_manager_escalation_id or 'pending'}\n\n"
            "Current email:\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject or '(no subject)'}\n"
            f"Body: {email.body or '(empty body)'}"
        )
        if self.dry_run:
            return (
                "Dry-run: would draft retention reply using thread context and policy excerpts.",
                None,
            )
        draft = self.tools.draft_retention_reply(context)
        state.retention_reply_text = draft
        return f"Retention reply drafted ({len(draft)} characters).", draft

    def _execute_final(
        self,
        state: AgentState,
        step: PlannedStep,
    ) -> tuple[str, str | None]:
        email = state.email
        final = step.final_action or step.action

        if final == "ignore":
            if self.dry_run:
                return f"Dry-run: would ignore email {email.id}.", None
            return f"Email {email.id} marked for ignore.", None

        if final == "create_internal_ticket":
            if state.ticket_id:
                return f"Ticket ready: {state.ticket_id}", state.ticket_body
            obs = self._create_ticket(state)
            return obs, state.ticket_body

        if final == "retention_draft_response":
            return self._draft_retention(state)

        if final == "draft_reply":
            context = (
                f"Thread history:\n{state.thread_history or ''}\n\n"
                f"Knowledge base:\n{state.rag_text or '(none)'}\n\n"
                "Current email:\n"
                f"From: {email.sender}\n"
                f"Subject: {email.subject or '(no subject)'}\n"
                f"Body: {email.body or '(empty body)'}"
            )
            if self.dry_run:
                return (
                    f"Dry-run: would draft reply using {len(state.rag_chunks)} KB chunk(s) "
                    f"and {len(state.thread_history or '')} characters of thread context.",
                    None,
                )
            draft = self.tools.draft_reply(context)
            state.draft_reply_text = draft
            return f"Draft reply generated ({len(draft)} characters).", draft

        if final == "escalate_to_human":
            return self._escalate(state, step)

        raise ValueError(f"Unknown final action: {final}")

    def _escalate(self, state: AgentState, step: PlannedStep) -> tuple[str, str | None]:
        email = state.email
        priority = max(
            email.priority_score,
            URGENCY_PRIORITY.get(email.urgency or "", 50),
        )
        reason = self._escalation_reason(state, step)

        proposed = state.retention_reply_text or state.holding_reply or state.draft_reply_text
        if self.dry_run:
            return f"Dry-run: would escalate with priority {priority}", proposed

        escalation = self.tools.escalate_to_human(state.email_id_str, reason, priority)
        if proposed is None:
            proposed = escalation["brief"]
        return f"Escalation queued: {escalation['escalation_id']}", proposed

    def _escalation_reason(self, state: AgentState, step: PlannedStep) -> str:
        if state.workflow == "bob_jones":
            account = state.account
            tier = account["subscription_tier"] if account else "unknown"
            renewal = account["renewal_status"] if account else "unknown"
            ticket = state.ticket_id or "pending"
            return (
                "SLA breach + legal review escalation. "
                f"Account {tier} (renewal {renewal}). "
                f"Internal ticket {ticket}. Legal flagged."
            )

        action = step.action
        if "reason=" in action:
            start = action.index("reason=") + len("reason=")
            fragment = action[start:]
            if fragment.startswith(("'", '"')):
                quote = fragment[0]
                end = fragment.index(quote, 1)
                return fragment[1:end]
        return "Escalation required per triage rules"
