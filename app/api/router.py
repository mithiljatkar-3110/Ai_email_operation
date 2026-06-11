from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.api.deps import get_ingest_service
from app.schemas.email import EmailIn, EmailResponse
from app.services.exceptions import DuplicateMessageError
from app.services.ingest_service import IngestService
from app.services.post_ingest import run_post_ingest_classification

api_router = APIRouter(prefix="/api", tags=["ingest"])


@api_router.post(
    "/ingest",
    response_model=EmailResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a new email",
)
def ingest_email(
    payload: EmailIn,
    background_tasks: BackgroundTasks,
    service: IngestService = Depends(get_ingest_service),
) -> EmailResponse:
    try:
        response = service.ingest(payload)
        background_tasks.add_task(run_post_ingest_classification, response.job_id)
        return response
    except DuplicateMessageError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "DUPLICATE_MESSAGE_ID",
                "message": str(exc),
                "details": {"message_id": exc.message_id},
            },
        ) from exc
