from fastapi import APIRouter, Depends, Query

from app.api.deps import get_dashboard_service
from app.schemas.dashboard import AgentActivityItem, DashboardStats, InboxItem
from app.services.dashboard_service import DashboardService

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Mission control dashboard KPIs",
)
def dashboard_stats(
    dashboard: DashboardService = Depends(get_dashboard_service),
) -> DashboardStats:
    return dashboard.get_stats()


@dashboard_router.get(
    "/inbox",
    response_model=list[InboxItem],
    summary="Paginated inbox feed (newest first)",
)
def dashboard_inbox(
    limit: int = Query(50, ge=1, le=200, description="Maximum rows to return"),
    offset: int = Query(0, ge=0, description="Number of rows to skip"),
    dashboard: DashboardService = Depends(get_dashboard_service),
) -> list[InboxItem]:
    return dashboard.get_inbox(limit=limit, offset=offset)


@dashboard_router.get(
    "/agent-activity",
    response_model=list[AgentActivityItem],
    summary="Recent agent actions (newest first)",
)
def dashboard_agent_activity(
    limit: int = Query(50, ge=1, le=200, description="Maximum actions to return"),
    dashboard: DashboardService = Depends(get_dashboard_service),
) -> list[AgentActivityItem]:
    return dashboard.get_agent_activity(limit=limit)
