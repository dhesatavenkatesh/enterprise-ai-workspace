from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.role import Role

DEFAULT_ROLES = [
    {
        "name": "Admin",
        "description": "Full system access",
    },
    {
        "name": "HR",
        "description": "Human resources module access",
    },
    {
        "name": "Employee",
        "description": "Standard employee access",
    },
    {
        "name": "Manager",
        "description": "Manager and team access",
    },
    {
        "name": "Support",
        "description": "Support module access",
    },
]


def seed_roles() -> None:
    db = SessionLocal()

    try:
        for role_data in DEFAULT_ROLES:
            existing_role = db.scalar(
                select(Role).where(
                    Role.name == role_data["name"],
                )
            )

            if existing_role is None:
                db.add(
                    Role(
                        name=role_data["name"],
                        description=role_data["description"],
                    )
                )

        db.commit()
        print("Default roles seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()
