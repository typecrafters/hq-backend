"""makemigrations — generate a new Alembic migration from model changes.

Usage:
    uv run python app/manage.py makemigrations <description>
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
VERSIONS = ROOT / "app" / "models" / "migrations" / "versions"


def _makemigrations(args: list[str]):
    message = " ".join(args)

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
    raise SystemExit(result.returncode)


def register(registry):
    registry.add(
        name="makemigrations",
        help="Generate a new Alembic migration from model changes",
        fn=_makemigrations,
        min_args=1,
    )
