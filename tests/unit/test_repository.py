"""Unit tests for the base Repository class.

Uses SQLite in-memory so no PostgreSQL is needed.
"""

import pytest
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from app.repositories.repository import Repository


class _RepoBase(DeclarativeBase):
    pass


class _RepoEntity(_RepoBase):
    __tablename__ = "test_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String, nullable=True)


@pytest.fixture
def engine():
    e = create_engine("sqlite:///:memory:", echo=False)
    _RepoBase.metadata.create_all(e)
    yield e
    e.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture
def repo(session):
    class TestRepo(Repository[_RepoEntity, int]):
        def __init__(self, db: Session):
            super().__init__(db, _RepoEntity)

    return TestRepo(session)


class TestRepository:
    """Coverage: Repository.get_by_id, save, get_all, get_by, find_by,
    exists, count, delete, delete_by_id, upsert.
    """

    def test_save_and_get_by_id(self, repo):
        entity = _RepoEntity(name="foo", email="foo@test.com")
        saved = repo.save(entity)
        assert saved.id is not None

        loaded = repo.get_by_id(saved.id)
        assert loaded is not None
        assert loaded.name == "foo"
        assert loaded.email == "foo@test.com"

    def test_get_by_id_returns_none_for_missing(self, repo):
        assert repo.get_by_id(999) is None

    def test_get_all_returns_all(self, repo):
        repo.save(_RepoEntity(name="a"))
        repo.save(_RepoEntity(name="b"))
        all_items = repo.get_all()
        assert len(all_items) >= 2

    def test_get_all_with_limit_offset(self, repo):
        for i in range(5):
            repo.save(_RepoEntity(name=f"item{i}"))
        limited = repo.get_all(limit=2, offset=0)
        assert len(limited) == 2

    def test_get_by_finds_existing(self, repo):
        repo.save(_RepoEntity(name="unique", email="u@test.com"))
        found = repo.get_by("name", "unique")
        assert found is not None
        assert found.email == "u@test.com"

    def test_get_by_returns_none_when_not_found(self, repo):
        found = repo.get_by("name", "nonexistent")
        assert found is None

    def test_get_by_raises_on_bad_attribute(self, repo):
        with pytest.raises(AttributeError, match="has no attribute"):
            repo.get_by("nonexistent", "val")

    def test_find_by_returns_matching(self, repo):
        repo.save(_RepoEntity(name="a", email="group@test.com"))
        repo.save(_RepoEntity(name="b", email="group@test.com"))
        results = repo.find_by("email", "group@test.com")
        assert len(results) == 2

    def test_find_by_raises_on_bad_attribute(self, repo):
        with pytest.raises(AttributeError, match="has no attribute"):
            repo.find_by("bad_attr", "x")

    def test_exists_returns_true(self, repo):
        entity = repo.save(_RepoEntity(name="exists"))
        assert repo.exists(entity.id) is True

    def test_exists_returns_false(self, repo):
        assert repo.exists(999) is False

    def test_count(self, repo):
        repo.save(_RepoEntity(name="a"))
        repo.save(_RepoEntity(name="b"))
        assert repo.count() >= 2

    def test_delete_removes_entity(self, repo):
        entity = repo.save(_RepoEntity(name="delete_me"))
        repo.delete(entity)
        assert repo.get_by_id(entity.id) is None

    def test_delete_by_id_returns_true(self, repo):
        entity = repo.save(_RepoEntity(name="del_by_id"))
        assert repo.delete_by_id(entity.id) is True

    def test_delete_by_id_returns_false(self, repo):
        assert repo.delete_by_id(999) is False

    def test_upsert_new_entity(self, repo):
        entity = _RepoEntity(name="upsert_new")
        merged = repo.upsert(entity)
        assert merged.id is not None

    def test_upsert_existing_entity(self, repo):
        entity = repo.save(_RepoEntity(name="original"))
        entity.name = "updated"
        merged = repo.upsert(entity)
        loaded = repo.get_by_id(merged.id)
        assert loaded is not None
        assert loaded.name == "updated"
