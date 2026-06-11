from fastapi import APIRouter, Depends

from app.api.deps import get_analytics_service
from app.schemas.analytics import (
    ConfidenceDistribution,
    EscalationRate,
    SentimentTrendPoint,
)
from app.services.analytics_service import AnalyticsService

analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])


@analytics_router.get(
    "/category-breakdown",
    response_model=dict[str, int],
    summary="Email count by classification category",
)
def category_breakdown(
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, int]:
    return analytics.category_breakdown()


@analytics_router.get(
    "/sentiment-trend",
    response_model=list[SentimentTrendPoint],
    summary="Average sentiment score grouped by day",
)
def sentiment_trend(
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> list[SentimentTrendPoint]:
    return analytics.sentiment_trend()


@analytics_router.get(
    "/escalation-rate",
    response_model=EscalationRate,
    summary="Share of emails escalated to humans",
)
def escalation_rate(
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> EscalationRate:
    return analytics.escalation_rate()


@analytics_router.get(
    "/action-distribution",
    response_model=dict[str, int],
    summary="Agent final action counts",
)
def action_distribution(
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, int]:
    return analytics.action_distribution()


@analytics_router.get(
    "/confidence-distribution",
    response_model=ConfidenceDistribution,
    summary="Classification confidence buckets",
)
def confidence_distribution(
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> ConfidenceDistribution:
    return analytics.confidence_distribution()
