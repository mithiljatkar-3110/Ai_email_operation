from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.classification_errors import raise_classification_http_error
from app.api.deps import get_classification_service
from app.schemas.classification import ClassificationResult
from app.services.classification_service import ClassificationService

test_router = APIRouter(prefix="/test", tags=["test"])


@test_router.post(
    "/classify/{email_id}",
    response_model=ClassificationResult,
    summary="Classify an email (test endpoint, does not persist)",
)
def test_classify_email(
    email_id: UUID,
    service: ClassificationService = Depends(get_classification_service),
) -> ClassificationResult:
    try:
        return service.classify_by_email_id(email_id)
    except Exception as exc:
        raise_classification_http_error(exc)
