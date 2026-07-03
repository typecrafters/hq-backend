from app.repositories.repository import Repository
from app.models.role import Role

class RoleRepository(Repository):
    def create_role(self, name: str, permissions: list[str], can_login: bool = False) -> Role:
        role = Role(
            name=name,
            permissions=permissions,
            can_login=can_login,
        )

        self.db.add(role)
        self.db.flush()
        return role
