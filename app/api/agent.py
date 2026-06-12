from uuid import UUID

from fastapi import APIRouter, Depends

from app.agents.triage_agent import TriageAgent
from app.api.agent_errors import raise_agent_http_error
from app.api.deps import get_triage_agent
from app.schemas.agent import AgentDryRunResponse, AgentExecuteResponse

agent_router = APIRouter(prefix="/agent", tags=["agent"])


@agent_router.post(
    "/dry-run/{email_id}",
    response_model=AgentDryRunResponse,
    summary="Run triage agent in dry-run mode (no DB writes)",
    description=(
        "Requires the email to already be classified: `category`, `urgency`, and "
        "`confidence` must be set (run `POST /api/classify/{email_id}` first). "
        "Returns 422 `TRIAGE_NOT_READY` otherwise. No actions are persisted in dry-run."
    ),
)
def agent_dry_run(
    email_id: UUID,
    agent: TriageAgent = Depends(get_triage_agent),
) -> AgentDryRunResponse:
    try:
        result = agent.run(email_id, dry_run=True)
        return AgentDryRunResponse(
            final_action=result.final_action,
            reasoning_trace=result.reasoning_trace,
        )
    except Exception as exc:
        raise_agent_http_error(exc)


@agent_router.post(
    "/execute/{email_id}",
    response_model=AgentExecuteResponse,
    summary="Run triage agent and persist the final action",
    description=(
        "Requires the email to already be classified: `category`, `urgency`, and "
        "`confidence` must be set (run `POST /api/classify/{email_id}` first). "
        "Executes the final action, saves the reasoning trace, and persists an "
        "action record in the Actions table."
    ),
)
def agent_execute(
    email_id: UUID,
    agent: TriageAgent = Depends(get_triage_agent),
) -> AgentExecuteResponse:
    try:
        result = agent.run(email_id, dry_run=False)
        return AgentExecuteResponse(
            final_action=result.final_action,
            action_saved=True,
        )
    except Exception as exc:
        raise_agent_http_error(exc)
