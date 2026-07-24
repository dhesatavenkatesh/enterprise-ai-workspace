import os

from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware


def configure_production_security(app: FastAPI) -> None:
    allowed_hosts = [
        host.strip()
        for host in os.getenv(
            "ALLOWED_HOSTS",
            "localhost,127.0.0.1,testserver",
        ).split(",")
        if host.strip()
    ]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )


def validate_required_secrets() -> None:
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment != "production":
        return

    required = [
        "DATABASE_URL",
        "SECRET_KEY",
        "GROQ_API_KEY",
        "REDIS_URL",
    ]
    missing = [name for name in required if not os.getenv(name)]

    if missing:
        raise RuntimeError(
            "Missing production environment variables: "
            + ", ".join(missing)
        )
