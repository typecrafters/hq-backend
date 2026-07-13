from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, Template

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / 'templates'

class TemplateFile:
    template: Template

    def __init__(self, environment: Environment, filename: str):
        self.template = environment.get_template(filename)

    def plain(self) -> str:
        return self.template.render()

    def using(self, data: dict[str, Any] = {}):
        return self.template.render(**data)

class TemplatingService:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=True
    )

    @classmethod
    def render(cls, filename: str):
        return TemplateFile(cls.env, filename)

