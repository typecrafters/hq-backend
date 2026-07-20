"""Add lang column and composite unique (slug, lang) to posts

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-20 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0008'
down_revision: Union[str, Sequence[str], None] = '0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('lang', sa.String(length=5), nullable=False, server_default='en'))
    op.drop_index('ix_posts_slug', table_name='posts')
    op.create_index('ix_posts_slug_lang', 'posts', ['slug', 'lang'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_posts_slug_lang', table_name='posts')
    op.create_index(op.f('ix_posts_slug'), 'posts', ['slug'], unique=True)
    op.drop_column('posts', 'lang')
