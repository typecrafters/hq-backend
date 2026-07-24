"""Lowercase (camelCase) poststatus enum values

Revision ID: 0012
Revises: 0011
Create Date: 2026-07-24 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op


revision: str = '0012'
down_revision: Union[str, None] = '0011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_RENAMES = [
    ('Published', 'published'),
    ('Draft', 'draft'),
    ('Archived', 'archived'),
]


def upgrade() -> None:
    for old, new in _RENAMES:
        op.execute(f"ALTER TYPE poststatus RENAME VALUE '{old}' TO '{new}'")


def downgrade() -> None:
    for old, new in _RENAMES:
        op.execute(f"ALTER TYPE poststatus RENAME VALUE '{new}' TO '{old}'")
