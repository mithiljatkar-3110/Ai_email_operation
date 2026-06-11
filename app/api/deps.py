from fastapi import Depends
from sqlalchemy.orm import Session

from app.agents.triage_agent import TriageAgent
from app.db.database import get_db
from app.rag.retriever import Retriever, get_retriever as get_default_retriever
from app.services.analytics_service import AnalyticsService
from app.services.dashboard_service import DashboardService
from app.services.classification_service import ClassificationService
from app.services.ingest_service import IngestService
from app.services.llm_classifier import LLMClassifier, get_llm_classifier
from app.services.thread_context_service import ThreadContextService
from app.services.thread_workspace_service import ThreadWorkspaceService


def get_ingest_service(db: Session = Depends(get_db)) -> IngestService:
    return IngestService(db)


def get_thread_context_service(db: Session = Depends(get_db)) -> ThreadContextService:
    return ThreadContextService(db)


def get_llm_classifier_dependency() -> LLMClassifier:
    return get_llm_classifier()


def get_retriever() -> Retriever:
    return get_default_retriever()


def get_classification_service(
    db: Session = Depends(get_db),
    thread_context_service: ThreadContextService = Depends(get_thread_context_service),
    retriever: Retriever = Depends(get_retriever),
    llm_classifier: LLMClassifier = Depends(get_llm_classifier_dependency),
) -> ClassificationService:
    return ClassificationService(
        db=db,
        thread_context_service=thread_context_service,
        retriever=retriever,
        llm_classifier=llm_classifier,
    )


def get_triage_agent(db: Session = Depends(get_db)) -> TriageAgent:
    return TriageAgent(db)


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


def get_thread_workspace_service(db: Session = Depends(get_db)) -> ThreadWorkspaceService:
    return ThreadWorkspaceService(db)
