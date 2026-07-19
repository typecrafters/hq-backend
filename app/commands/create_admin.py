"""create-admin — create an admin user in the database.

Usage:
    uv run python app/manage.py create-admin [email] [password]

Defaults:
    email:    admin@typecrafters.com
    password: Admin123!
"""
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.role import Role
from app.models.user import User
from app.services.static.password_service import PasswordService


DEFAULT_EMAIL = "admin@typecrafters.com"
DEFAULT_PASSWORD = "Admin123!"


def _create_admin(args: list[str]):
    email = args[0] if len(args) > 0 else DEFAULT_EMAIL
    password = args[1] if len(args) > 1 else DEFAULT_PASSWORD

    engine = create_engine(settings.database_url())

    with Session(engine) as session:
        # Create admin role if it doesn't exist
        role = session.execute(
            select(Role).where(Role.name == "admin")
        ).scalar_one_or_none()

        if role is None:
            role = Role(
                name="admin",
                permissions=["read:message", "write:message", "delete:message", "read:user", "write:user", "delete:user", "write:role", "write:media", "read:post", "write:post", "delete:post"],
                can_login=True,
            )
            session.add(role)
            session.flush()
            print(f"  Role 'admin' created (id={role.id})")
        else:
            print(f"  Role 'admin' exists (id={role.id})")

        # Check if user already exists
        existing = session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing is not None:
            print(f"  User '{email}' already exists (id={existing.id})")
            return

        # Create user
        hashed = PasswordService.hash(password)
        user = User(
            role_id=role.id,
            first_name="Admin",
            last_name="User",
            email=email,
            password=hashed,
            created_at=datetime.now(timezone.utc),
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"\n  Admin user created!")
        print(f"  Email:    {email}")
        print(f"  Password: {password}")
        print(f"  User ID:  {user.id}")


def register(registry):
    registry.add(
        name="create-admin",
        help="Create an admin user (default: admin@typecrafters.com / Admin123!)",
        fn=_create_admin,
    )
