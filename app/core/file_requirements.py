from dataclasses import dataclass
from typing import Self

from app.core.util import Storage


@dataclass(frozen=True)
class FileRequirementsResult:
    ok: bool
    status_code: int | None = None
    detail: str | None = None


class FileRequirements:
    allowed_types: list[str]
    max_file_size: Storage

    def __init__(self, allowed_types: list[str], max_file_size: Storage):
        self.allowed_types = allowed_types
        self.max_file_size = max_file_size

    @classmethod
    def images(cls) -> Self:
        return cls(allowed_types=['image/*'], max_file_size=Storage.of_mb(5))

    @classmethod
    def posts(cls) -> Self:
        return cls(allowed_types=['text/markdown', 'application/json'], max_file_size=Storage.of_mb(10))

    def __accepts_type(self, content_type: str) -> bool:
        for allowed in self.allowed_types:
            if allowed.endswith('/*'):
                if content_type.split('/', 1)[0] == allowed[:-2]:
                    return True
            elif allowed == content_type:
                return True
        return False

    def are_met(self, content_type: str, size: int) -> FileRequirementsResult:
        if not self.__accepts_type(content_type):
            return FileRequirementsResult(
                ok=False,
                status_code=415,
                detail=f"Unsupported file type '{content_type}'. Allowed types: {', '.join(self.allowed_types)}."
            )
        if size > self.max_file_size.to_b():
            return FileRequirementsResult(
                ok=False,
                status_code=413,
                detail=f"File exceeds the maximum size of {self.max_file_size.to_mb():.0f}MB."
            )
        return FileRequirementsResult(ok=True)
