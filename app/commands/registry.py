"""Command registry — discovers and executes management commands.

Usage:
    registry = CommandRegistry()
    registry.autodiscover()
    registry.run(sys.argv[1:])
"""
from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class Command:
    name: str
    help: str
    fn: Callable[[list[str]], None]
    min_args: int = 0


class CommandRegistry:
    def __init__(self):
        self._commands: dict[str, Command] = {}

    def add(self, name: str, help: str, fn: Callable[[list[str]], None], min_args: int = 0):
        self._commands[name] = Command(name=name, help=help, fn=fn, min_args=min_args)

    def autodiscover(self):
        """Import all modules in app.commands so their register() runs."""
        package = importlib.import_module("app.commands")
        package_path = Path(package.__file__).parent

        for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
            if module_name.startswith("_"):
                continue
            mod = importlib.import_module(f"app.commands.{module_name}")
            if hasattr(mod, "register"):
                mod.register(self)

    def run(self, args: list[str]):
        if not args or args[0] in ("-h", "--help"):
            self._print_help()
            return

        name = args[0]
        cmd = self._commands.get(name)
        if cmd is None:
            print(f"Unknown command: {name}")
            self._print_help()
            raise SystemExit(1)

        if len(args) - 1 < cmd.min_args:
            print(f"Error: '{name}' requires at least {cmd.min_args} argument(s).")
            raise SystemExit(1)

        cmd.fn(args[1:])

    def _print_help(self):
        print("Usage: uv run python app/manage.py <command> [args]\n")
        print("Commands:")
        for cmd in sorted(self._commands.values(), key=lambda c: c.name):
            print(f"  {cmd.name:<25s} {cmd.help}")
