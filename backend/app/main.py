from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all SQLAlchemy models before create_all.
from app.database import models  # noqa: F401
from app.database.base import Base
from app.database.session import engine
from app.api.rag import router as rag_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.prompt_templates import (
    router as prompt_templates_router,
)
from app.api.routes.mcp import router as mcp_router
from app.api.documents import router as documents_router
from app.api.routes.rbac import router as rbac_router
from app.chat.chat_api import router as chat_router
from app.api.routes.chat_analytics import (
    router as chat_analytics_router,
)
from app.api.routes.orchestrator import (
    router as orchestrator_router,
)
from app.api.routes.workflows import router as workflows_router
from app.api.routes.agents import router as agents_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.sprint4_health import (
    router as sprint4_health_router,
)
from app.api.routes.agent_analytics import (
    router as agent_analytics_router,
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI startup and shutdown lifecycle.
    """

    print("Starting Enterprise AI Workspace backend...")

    # Suitable for local development.
    # Alembic migrations should be used in production.
    Base.metadata.create_all(bind=engine)

    print("Database tables verified successfully.")

    yield

    print("Shutting down Enterprise AI Workspace backend...")


app = FastAPI(
    title="Enterprise AI Workspace API",
    description=(
        "Enterprise AI platform with authentication, RBAC, "
        "AI chat, conversations, prompt templates and analytics."
    ),
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(rbac_router)
app.include_router(chat_router)
app.include_router(prompt_templates_router)
app.include_router(chat_analytics_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(agents_router)
app.include_router(mcp_router)
app.include_router(workflows_router)
app.include_router(approvals_router)
app.include_router(sprint4_health_router)
app.include_router(agent_analytics_router)
app.include_router(
    orchestrator_router,
)

@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {
        "message": "Enterprise AI Workspace API is running",
        "version": "4.0.0",
        "documentation": "/docs",
    }
