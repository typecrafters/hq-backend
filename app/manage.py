"""Django-like management commands.

Usage:
    uv run python manage.py makemigrations "description"
    uv run python manage.py migrate
"""

import sys
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSIONS = ROOT / "app" / "models" / "migrations" / "versions"


def makemigrations(message: str):
    max_num = 0
    if VERSIONS.exists():
        for f in VERSIONS.iterdir():
            if f.suffix == ".py" and f.name != "__init__.py":
                m = re.match(r"^(\d{4})_", f.name)
                if m:
                    max_num = max(max_num, int(m.group(1)))

    rev_id = f"{max_num + 1:04d}"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message, "--rev-id", rev_id],
        cwd=ROOT,
    )
    sys.exit(result.returncode)


def migrate():
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python manage.py <command> [args]")
        print()
        print("Commands:")
        print("  makemigrations <description>   = makemigrations")
        print("  migrate                         = migrate")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "makemigrations" and len(sys.argv) >= 3:
        makemigrations(" ".join(sys.argv[2:]))
    elif cmd == "migrate":
        migrate()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
