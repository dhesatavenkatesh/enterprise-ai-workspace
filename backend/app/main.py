from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.admin.router import router as admin_router
from app.api.admin_permissions import router as admin_permissions_router
from app.api.documents import router as documents_router
from app.api.rag import router as rag_router
from app.api.routes.agent_analytics import router as agent_analytics_router
from app.api.routes.agents import router as agents_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chat_analytics import router as chat_analytics_router
from app.api.routes.health import router as health_router
from app.api.routes.mcp import router as mcp_router
from app.api.routes.orchestrator import router as orchestrator_router
from app.api.routes.prompt_templates import router as prompt_templates_router
from app.api.routes.rbac import router as rbac_router
from app.api.routes.sprint4_health import router as sprint4_health_router
from app.api.routes.workflows import router as workflows_router
from app.chat.chat_api import router as chat_router
from app.database import models  # noqa: F401
from app.database.base import Base
from app.database.session import engine
from app.monitoring.middleware import PrometheusMiddleware
from app.security.middleware import SecurityHeadersMiddleware
from app.security.rate_limit import limiter
from app.api.routes.cache_health import router as cache_health_router
from app.core.error_handlers import register_error_handlers
from app.core.logging_config import configure_logging
from app.middleware.body_limit import RequestBodyLimitMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.security.production import (
    configure_production_security,
    validate_required_secrets,
)
load_dotenv()
configure_logging()
validate_required_secrets()

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Handle application startup and shutdown tasks."""

    print("Starting Enterprise AI Workspace backend...")

    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables verified successfully.")
    except Exception as exc:
        print(f"Database initialization failed: {exc}")
        raise

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

    print("Security middleware enabled.")
    print("Prometheus monitoring enabled at /metrics.")
    print("API rate limiting enabled.")

    yield

    print("Shutting down Enterprise AI Workspace backend...")


app = FastAPI(
    title="Enterprise AI Workspace API",
    description=(
        "Enterprise AI platform with authentication, RBAC, "
        "AI chat, administration, monitoring and analytics."
    ),
    version="6.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

register_error_handlers(app)
configure_production_security(app)

app.add_middleware(
    RequestBodyLimitMiddleware,
    max_body_size=10 * 1024 * 1024,
)
app.add_middleware(RequestLoggingMiddleware)
# ---------------------------------------------------------
# Security and monitoring middleware
# ---------------------------------------------------------

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(PrometheusMiddleware)
app.include_router(cache_health_router)

# ---------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
)


# ---------------------------------------------------------
# Authentication, health and RBAC
# ---------------------------------------------------------

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(rbac_router)


# ---------------------------------------------------------
# Sprint 5 administration
# ---------------------------------------------------------

app.include_router(admin_router)
app.include_router(admin_permissions_router)


# ---------------------------------------------------------
# Chat and prompt management
# ---------------------------------------------------------

app.include_router(chat_router)
app.include_router(prompt_templates_router)
app.include_router(chat_analytics_router)


# ---------------------------------------------------------
# Documents and RAG
# ---------------------------------------------------------

app.include_router(documents_router)
app.include_router(rag_router)


# ---------------------------------------------------------
# Agents, MCP and workflows
# ---------------------------------------------------------

app.include_router(agents_router)
app.include_router(mcp_router)
app.include_router(workflows_router)
app.include_router(approvals_router)
app.include_router(orchestrator_router)


# ---------------------------------------------------------
# Monitoring and analytics
# ---------------------------------------------------------

app.include_router(sprint4_health_router)
app.include_router(agent_analytics_router)


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get(
    "/",
    tags=["Root"],
    summary="API root endpoint",
)
def root() -> dict[str, str]:
    """Return basic API information."""

    return {
        "message": "Enterprise AI Workspace API is running",
        "version": app.version,
        "documentation": "/docs",
        "health": "/system/health",
        "metrics": "/metrics",
    }


# ---------------------------------------------------------
# Production health endpoint
# ---------------------------------------------------------

@app.get(
    "/system/health",
    tags=["System"],
    summary="Production health check",
)
async def production_health_check() -> dict[str, str]:
    """Return the production health status."""

    return {
        "status": "healthy",
        "service": "enterprise-ai-workspace-backend",
        "version": app.version,
    }


# ---------------------------------------------------------
# Registered routes development endpoint
# ---------------------------------------------------------

@app.get(
    "/api/routes",
    tags=["Development"],
    summary="List registered API routes",
    include_in_schema=False,
)
def list_registered_routes() -> dict[str, list[dict[str, object]]]:
    """Return all registered FastAPI routes."""

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

    routes.sort(key=lambda route: str(route["path"]))

    return {
        "routes": routes,
    }


# ---------------------------------------------------------
# Prometheus metrics
# ---------------------------------------------------------

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)