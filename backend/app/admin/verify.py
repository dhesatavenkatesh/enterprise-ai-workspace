from typing import Any

from fastapi import FastAPI
from sqlalchemy.orm import configure_mappers

import app.models  # noqa: F401
from app.admin.router import router as admin_router
from app.main import app as fastapi_app


EXPECTED_ADMIN_ROUTES = {
    "/api/admin/users",
    "/api/admin/users/{user_id}",
    "/api/admin/users/{user_id}/status",
    "/api/admin/users/{user_id}/activate",
    "/api/admin/users/{user_id}/deactivate",
    "/api/admin/users/{user_id}/lock",
    "/api/admin/users/{user_id}/unlock",
    "/api/admin/users/{user_id}/reset-password",
    "/api/admin/roles",
    "/api/admin/roles/permissions",
    "/api/admin/roles/{role_id}",
    "/api/admin/roles/{role_id}/permissions",
    "/api/admin/dashboard",
    "/api/admin/audit-logs",
    "/api/admin/audit-logs/{audit_log_id}",
}


def verify_fastapi_instance(
    application: FastAPI,
) -> None:
    if not isinstance(application, FastAPI):
        raise TypeError(
            "fastapi_app is not a FastAPI instance. "
            f"Received: {type(application).__name__}"
        )

    print("✓ FastAPI application instance loaded successfully")


def verify_sqlalchemy_models() -> None:
    configure_mappers()

    print("✓ SQLAlchemy models configured successfully")


def verify_admin_router_prefix() -> None:
    if admin_router.prefix != "/api/admin":
        raise RuntimeError(
            "Admin router prefix must be '/api/admin'. "
            f"Current prefix: {admin_router.prefix!r}"
        )

    print("✓ Admin router prefix is correct")


def get_openapi_paths(
    application: FastAPI,
) -> dict[str, Any]:
    # Clear any previously cached OpenAPI schema.
    application.openapi_schema = None

    schema = application.openapi()

    paths = schema.get("paths", {})

    if not isinstance(paths, dict):
        raise RuntimeError(
            "FastAPI OpenAPI schema does not contain a valid paths object."
        )

    return paths


def get_admin_paths(
    application: FastAPI,
) -> dict[str, Any]:
    paths = get_openapi_paths(application)

    return {
        path: operations
        for path, operations in paths.items()
        if path.startswith("/api/admin")
    }


def verify_duplicate_prefixes(
    application: FastAPI,
) -> None:
    paths = get_openapi_paths(application)

    invalid_paths = [
        path
        for path in paths
        if "/api/admin/api/admin" in path
    ]

    if invalid_paths:
        print("✗ Duplicate admin prefixes found:")

        for path in sorted(invalid_paths):
            print(f"  - {path}")

        raise RuntimeError(
            "Duplicate '/api/admin' prefix detected"
        )

    print("✓ No duplicate /api/admin prefixes found")


def verify_admin_routes(
    application: FastAPI,
) -> None:
    admin_paths = get_admin_paths(application)

    registered_paths = set(admin_paths)

    missing_paths = (
        EXPECTED_ADMIN_ROUTES
        - registered_paths
    )

    if missing_paths:
        print("✗ Missing admin routes:")

        for path in sorted(missing_paths):
            print(f"  - {path}")

        print("\nCurrently registered admin routes:")

        if registered_paths:
            for path in sorted(registered_paths):
                print(f"  - {path}")
        else:
            print("  No admin routes are present in OpenAPI.")

        raise RuntimeError(
            "Sprint 5 admin route verification failed"
        )

    print(
        "✓ All expected Sprint 5 admin routes "
        "are registered"
    )


def print_admin_routes(
    application: FastAPI,
) -> None:
    admin_paths = get_admin_paths(application)

    print("\nRegistered Sprint 5 admin routes:")

    if not admin_paths:
        print("  No Sprint 5 admin routes found.")
        return

    for path in sorted(admin_paths):
        operations = admin_paths[path]

        if not isinstance(operations, dict):
            print(f"  UNKNOWN      {path}")
            continue

        methods = [
            method.upper()
            for method in operations
            if method.lower()
            in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
            }
        ]

        method_text = ", ".join(sorted(methods))

        print(f"  {method_text:<22} {path}")


def main() -> None:
    print("\nSprint 5 Admin Module Verification\n")

    verify_fastapi_instance(fastapi_app)
    verify_sqlalchemy_models()
    verify_admin_router_prefix()
    verify_duplicate_prefixes(fastapi_app)
    verify_admin_routes(fastapi_app)
    print_admin_routes(fastapi_app)

    print(
        "\n✓ Sprint 5 Admin module verification "
        "completed successfully\n"
    )


if __name__ == "__main__":
    main()