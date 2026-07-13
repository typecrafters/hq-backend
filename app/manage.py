"""Django-like management commands.

Usage:
    uv run python app/manage.py <command> [args]

Commands are auto-discovered from app/commands/. To add a new command,
create a module in app/commands/ with a register(registry) function.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.commands.registry import CommandRegistry


def main():
    registry = CommandRegistry()
    registry.autodiscover()
    registry.run(sys.argv[1:])


if __name__ == "__main__":
    main()
