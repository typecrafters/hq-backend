from sqlalchemy.orm import Session

from app.models.role import Role
from app.repositories.repository import Repository

class RoleRepository(Repository[Role, int]):
    def __init__(self, db: Session):
        super().__init__(db, Role)