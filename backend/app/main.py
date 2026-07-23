from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import models  # noqa: F401
from app.database.base import Base
from app.database.session import engine

from app.admin.router import router as admin_router
from app.api.documents import router as documents_router
from app.api.rag import router as rag_router
from app.api.routes.agent_analytics import (
    router as agent_analytics_router,
)
from app.api.routes.agents import router as agents_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chat_analytics import (
    router as chat_analytics_router,
)
from app.api.routes.health import router as health_router
from app.api.routes.mcp import router as mcp_router
from app.api.routes.orchestrator import (
    router as orchestrator_router,
)
from app.api.routes.prompt_templates import (
    router as prompt_templates_router,
)
from app.api.routes.rbac import router as rbac_router
from app.api.routes.sprint4_health import (
    router as sprint4_health_router,
)
from app.api.routes.workflows import router as workflows_router
from app.chat.chat_api import router as chat_router
from app.api.admin_permissions import (
    router as admin_permissions_router,
)

@asynccontextmanager
async def lifespan(application: FastAPI):
    print("Starting Enterprise AI Workspace backend...")

    Base.metadata.create_all(bind=engine)

    print("Database tables verified successfully.")

    admin_paths = [
        route.path
        for route in application.routes
        if getattr(route, "path", "").startswith("/api/admin")
    ]

    if admin_paths:
        print("Sprint 5 admin routes registered successfully:")

        for path in admin_paths:
            print(f"  - {path}")
    else:
        print(
            "WARNING: No Sprint 5 admin routes are registered. "
            "Check app/admin/router.py."
        )

    yield

    print("Shutting down Enterprise AI Workspace backend...")


app = FastAPI(
    title="Enterprise AI Workspace API",
    description=(
        "Enterprise AI platform with authentication, RBAC, "
        "AI chat, administration, monitoring and analytics."
    ),
    version="5.0.0",
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


# Authentication, health and RBAC
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(rbac_router)


# Sprint 5 administration
app.include_router(admin_router)
app.include_router(admin_permissions_router)

# Chat and prompt management
app.include_router(chat_router)
app.include_router(prompt_templates_router)
app.include_router(chat_analytics_router)


# Documents and RAG
app.include_router(documents_router)
app.include_router(rag_router)


# Agents, MCP and workflows
app.include_router(agents_router)
app.include_router(mcp_router)
app.include_router(workflows_router)
app.include_router(approvals_router)
app.include_router(orchestrator_router)


# Monitoring and analytics
app.include_router(sprint4_health_router)
app.include_router(agent_analytics_router)


@app.get(
    "/",
    tags=["Root"],
    summary="API root endpoint",
)
def root() -> dict[str, str]:
    return {
        "message": "Enterprise AI Workspace API is running",
        "version": "5.0.0",
        "documentation": "/docs",
    }


@app.get(
    "/api/routes",
    tags=["Development"],
    summary="List registered API routes",
    include_in_schema=False,
)
def list_registered_routes() -> dict[str, list[dict[str, object]]]:
    routes: list[dict[str, object]] = []

    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        name = getattr(route, "name", None)

        if path is None:
            continue

        routes.append(
            {
                "path": path,
                "methods": sorted(methods) if methods else [],
                "name": name,
            }
        )

    return {
        "routes": routes,
    }