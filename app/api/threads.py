from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_thread_workspace_service
from app.schemas.thread import ThreadWorkspaceResponse
from app.services.exceptions import ThreadNotFoundError
from app.services.thread_workspace_service import ThreadWorkspaceService

threads_router = APIRouter(prefix="/threads", tags=["threads"])


@threads_router.get(
    "/{thread_id}/workspace",
    response_model=ThreadWorkspaceResponse,
    summary="Thread workspace view (emails, classification, agent activity)",
)
def thread_workspace(
    thread_id: str,
    workspace: ThreadWorkspaceService = Depends(get_thread_workspace_service),
) -> ThreadWorkspaceResponse:
    try:
        return workspace.get_workspace(thread_id)
    except ThreadNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "THREAD_NOT_FOUND",
                "message": str(exc),
                "details": {"thread_id": exc.thread_id},
            },
        ) from exc
