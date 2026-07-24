"""Lowercase (camelCase) projectstatus enum values

Revision ID: 0011
Revises: 0010
Create Date: 2026-07-24 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op


revision: str = '0011'
down_revision: Union[str, None] = '0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_RENAMES = [
    ('Development', 'development'),
    ('Planned', 'planned'),
    ('Review', 'review'),
    ('Archived', 'archived'),
    ('Canceled', 'canceled'),
]


def upgrade() -> None:
    for old, new in _RENAMES:
        op.execute(f"ALTER TYPE projectstatus RENAME VALUE '{old}' TO '{new}'")


def downgrade() -> None:
    for old, new in _RENAMES:
        op.execute(f"ALTER TYPE projectstatus RENAME VALUE '{new}' TO '{old}'")
