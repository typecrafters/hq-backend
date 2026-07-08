from typing import Any

from pydantic import BaseModel

class ItemResponse[T](BaseModel):
    message: str
    item: T
    meta: dict[str, Any] | None = None