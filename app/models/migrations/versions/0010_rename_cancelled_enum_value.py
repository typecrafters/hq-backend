"""Rename projectstatus enum value Cancelled to Canceled

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-24 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op


revision: str = '0010'
down_revision: Union[str, None] = '0009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE projectstatus RENAME VALUE 'Cancelled' TO 'Canceled'")


def downgrade() -> None:
    op.execute("ALTER TYPE projectstatus RENAME VALUE 'Canceled' TO 'Cancelled'")
