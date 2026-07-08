from typing import Any, Protocol, runtime_checkable
from abc import ABC
from sqlalchemy import func, select
from sqlalchemy.orm import Session, Mapped


@runtime_checkable
class HasID[U](Protocol):
    id: Mapped[U]


class Repository[T: HasID, U](ABC):
    db: Session
    entity: type[T]

    def __init__(self, db: Session, entity: type[T]):
        self.db = db
        self.entity = entity

    def get_all(self, limit: int | None = None, offset: int | None = None) -> list[T]:
        stmt = select(self.entity).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, id: U) -> T | None:
        stmt = select(self.entity).where(self.entity.id == id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_by(self, attr: str, value: Any) -> T | None:
        if not hasattr(self.entity, attr):
            raise AttributeError(f"Entity '{self.entity.__name__}' has no attribute '{attr}'.")
        stmt = select(self.entity).where(getattr(self.entity, attr) == value).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def find_by(self, attr: str, value: Any) -> list[T]:
        if not hasattr(self.entity, attr):
            raise AttributeError(f"Entity '{self.entity.__name__}' has no attribute '{attr}'.")
        stmt = select(self.entity).where(getattr(self.entity, attr) == value)
        return list(self.db.execute(stmt).scalars().all())

    def exists(self, id: U) -> bool:
        stmt = select(1).select_from(self.entity).where(self.entity.id == id)
        return self.db.execute(stmt).scalar_one_or_none() is not None
    
    def count(self) -> int:
        stmt = select(func.count()).select_from(self.entity)
        return self.db.execute(stmt).scalar() or 0
    
    def save(self, entity: T) -> T:
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, entity: T) -> None:
        self.db.delete(entity)
        self.db.flush()

    def delete_by_id(self, id: U) -> bool:
        entity = self.get_by_id(id)
        if entity is None:
            return False
        self.delete(entity)
        return True

    def upsert(self, entity: T) -> T:
        merged = self.db.merge(entity)
        self.db.flush()
        return merged

    def update(self, id: U, **changes: Any) -> T | None:
        entity = self.get_by_id(id)
        if entity is None:
            return None

        for attr, value in changes.items():
            setattr(entity, attr, value)

        return self.save(entity)
