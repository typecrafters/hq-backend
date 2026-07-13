"""migrate — apply all pending Alembic migrations.

Usage:
    uv run python app/manage.py migrate
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def _migrate(args: list[str]):
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
    )
    raise SystemExit(result.returncode)


def register(registry):
    registry.add(
        name="migrate",
        help="Apply all pending Alembic migrations",
        fn=_migrate,
    )
