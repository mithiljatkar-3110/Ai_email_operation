from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.agent import agent_router
from app.api.analytics import analytics_router
from app.api.dashboard import dashboard_router
from app.api.classification import classification_router
from app.api.rag import rag_router
from app.api.router import api_router
from app.api.test import test_router
from app.api.threads import threads_router
from app.core.config import settings
from app.db.database import check_database_connection, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(classification_router)
app.include_router(agent_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)
app.include_router(rag_router)
app.include_router(test_router)
app.include_router(threads_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, Any]:
    """Liveness and readiness probe for orchestrators and load balancers."""
    payload: dict[str, Any] = {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.app_version,
        "database": "up",
    }

    try:
        check_database_connection()
    except SQLAlchemyError:
        payload["status"] = "degraded"
        payload["database"] = "down"
        return JSONResponse(status_code=503, content=payload)

    return payload
