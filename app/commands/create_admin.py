"""create-admin — create an admin user in the database.

Usage:
    uv run python app/manage.py create-admin [email] [password]

If email and password are omitted, both are randomly generated and printed
once at creation time. There are no hardcoded default credentials — passing
nothing is safe, but you must save the printed credentials immediately.

Idempotent: re-running is safe. If the admin role already exists, its
permissions are synced (union) with the canonical list below — existing
custom permissions are preserved. The user is created only if missing.
"""
import secrets
import string
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.role import Role
from app.models.user import User
from app.services.static.password_service import PasswordService


_EMAIL_LOCAL_LENGTH = 12
_EMAIL_DOMAIN = "typecrafters.com"
_PASSWORD_ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*"
_PASSWORD_LENGTH = 20


CANONICAL_ADMIN_PERMISSIONS: list[str] = [
    "read:message", "write:message", "delete:message",
    "read:user", "write:user", "delete:user",
    "read:role", "write:role",
    "read:post", "write:post", "delete:post",
    "read:project", "write:project", "delete:project",
    "write:media",
    "write:legal",
]


def _generate_email(local_length: int = _EMAIL_LOCAL_LENGTH, domain: str = _EMAIL_DOMAIN) -> str:
    """Generate a random admin email like 'adm-k7q9x2p4r8@typecrafters.com'."""
    alphabet = string.ascii_lowercase + string.digits
    local = "adm-" + "".join(secrets.choice(alphabet) for _ in range(local_length))
    return f"{local}@{domain}"


def _generate_password(length: int = _PASSWORD_LENGTH) -> str:
    """Generate a cryptographically secure random password."""
    return "".join(secrets.choice(_PASSWORD_ALPHABET) for _ in range(length))


def _sync_admin_role(session: Session, role: Role) -> None:
    merged = sorted(set(role.permissions or []) | set(CANONICAL_ADMIN_PERMISSIONS))
    if set(merged) != set(role.permissions or []):
        added = sorted(set(merged) - set(role.permissions or []))
        role.permissions = merged
        session.flush()
        if added:
            print(f"  Role 'admin' permissions synced (added: {', '.join(added)})")
        else:
            print("  Role 'admin' permissions synced")


def _create_admin(args: list[str]):
    generated_email = False
    if len(args) > 0:
        email = args[0]
    else:
        email = _generate_email()
        generated_email = True

    generated_password = False
    if len(args) > 1:
        password = args[1]
    else:
        password = _generate_password()
        generated_password = True

    engine = create_engine(settings.db_url)

    with Session(engine) as session:
        # Upsert admin role and sync its permissions to the canonical list.
        role = session.execute(
            select(Role).where(Role.name == "admin")
        ).scalar_one_or_none()

        if role is None:
            role = Role(
                name="admin",
                permissions=list(CANONICAL_ADMIN_PERMISSIONS),
                can_login=True,
            )
            session.add(role)
            session.flush()
            print(f"  Role 'admin' created (id={role.id})")
        else:
            print(f"  Role 'admin' exists (id={role.id})")
            _sync_admin_role(session, role)

        # Check if user already exists
        existing = session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing is not None:
            print(f"  User '{email}' already exists (id={existing.id})")
            session.commit()
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
        if generated_email or generated_password:
            print(
                "  (credentials were randomly generated — save them now, "
                "they will not be shown again)"
            )
        print(f"  User ID:  {user.id}")


def register(registry):
    registry.add(
        name="create-admin",
        help="Create an admin user (random email and password if not provided)",
        fn=_create_admin,
    )
