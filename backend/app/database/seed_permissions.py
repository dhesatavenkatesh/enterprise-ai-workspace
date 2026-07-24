from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

PERMISSIONS = [
    {
        "permission_name": "admin.full_access",
        "module": "admin",
        "description": "Full administrative access",
    },
    {
        "permission_name": "hr.access",
        "module": "hr",
        "description": "Access HR module",
    },
    {
        "permission_name": "chat.access",
        "module": "ai_chat",
        "description": "Access AI chat",
    },
    {
        "permission_name": "manager.access",
        "module": "manager",
        "description": "Access manager module",
    },
    {
        "permission_name": "support.access",
        "module": "support",
        "description": "Access support module",
    },
]


ROLE_PERMISSION_MAP = {
    "Admin": [
        "admin.full_access",
        "hr.access",
        "chat.access",
        "manager.access",
        "support.access",
    ],
    "HR": [
        "hr.access",
        "chat.access",
    ],
    "Employee": [
        "chat.access",
    ],
    "Manager": [
        "manager.access",
        "chat.access",
    ],
    "Support": [
        "support.access",
        "chat.access",
    ],
}


def seed_permissions() -> None:
    db = SessionLocal()

    try:
        for permission_data in PERMISSIONS:
            permission = db.scalar(
                select(Permission).where(
                    Permission.permission_name == permission_data["permission_name"]
                )
            )

            if permission is None:
                permission = Permission(
                    permission_name=(permission_data["permission_name"]),
                    module=permission_data["module"],
                    description=permission_data["description"],
                )

                db.add(permission)

        db.commit()

        for role_name, permission_names in ROLE_PERMISSION_MAP.items():
            role = db.scalar(select(Role).where(Role.name == role_name))

            if role is None:
                continue

            for permission_name in permission_names:
                permission = db.scalar(
                    select(Permission).where(Permission.permission_name == permission_name)
                )

                if permission is None:
                    continue

                mapping = db.scalar(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == permission.id,
                    )
                )

                if mapping is None:
                    db.add(
                        RolePermission(
                            role_id=role.id,
                            permission_id=permission.id,
                        )
                    )

        db.commit()

        print("Permissions and role mappings seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_permissions()
