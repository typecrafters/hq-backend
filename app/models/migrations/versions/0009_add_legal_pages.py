"""Add legal_pages table

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-20 23:50:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP


revision: str = '0009'
down_revision: Union[str, None] = '0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'legal_pages',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content_markdown', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_legal_pages_slug'), 'legal_pages', ['slug'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_legal_pages_slug'), table_name='legal_pages')
    op.drop_table('legal_pages')
