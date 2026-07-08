from typing import Any
from jinja2 import Environment, FileSystemLoader, Template

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
        loader=FileSystemLoader(),
        autoescape=True
    )

    @classmethod
    def render(cls, filename: str):
        return TemplateFile(cls.env, filename)

