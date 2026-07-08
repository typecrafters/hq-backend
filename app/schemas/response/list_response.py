from typing import Any

from pydantic import BaseModel

class ListResponse[T](BaseModel):
    message: str
    items: list[T]
    meta: dict[str, Any] | None = None