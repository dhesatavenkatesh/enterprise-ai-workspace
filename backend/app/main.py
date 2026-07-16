from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.routes.auth import (
    router as auth_router,
)
from app.api.routes.health import (
    router as health_router,
)
from app.api.routes.rbac import (
    router as rbac_router,
)
from app.core.config import settings
from app.core.exception_handlers import (
    register_exception_handlers,
)
from app.core.logging import setup_logging


setup_logging()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
)


allowed_origins = {
    settings.frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(
        allowed_origins,
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_exception_handlers(app)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(rbac_router)


@app.get(
    "/",
    tags=["Root"],
)
def root() -> dict[str, str]:
    return {
        "message": (
            "Enterprise AI Workspace API"
        ),
    }