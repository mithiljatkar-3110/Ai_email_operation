from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.classification_errors import raise_classification_http_error
from app.api.deps import get_classification_service
from app.schemas.classification import ClassificationResult
from app.services.classification_service import ClassificationService

classification_router = APIRouter(prefix="/api", tags=["classification"])


@classification_router.post(
    "/classify/{email_id}",
    response_model=ClassificationResult,
    summary="Run classification pipeline and save results",
)
def classify_and_save_email(
    email_id: UUID,
    service: ClassificationService = Depends(get_classification_service),
) -> ClassificationResult:
    try:
        return service.run_classification_pipeline(email_id)
    except Exception as exc:
        raise_classification_http_error(exc)
