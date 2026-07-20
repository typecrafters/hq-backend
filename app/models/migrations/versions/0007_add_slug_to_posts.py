"""Add slug to posts

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-20 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0007'
down_revision: Union[str, Sequence[str], None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('slug', sa.String(length=200), nullable=True))
    # Backfill existing rows with a slug derived from the id so the unique
    # constraint can be created without violating it.
    op.execute("UPDATE posts SET slug = 'post-' || id::text WHERE slug IS NULL")
    op.alter_column('posts', 'slug', nullable=False)
    op.create_index(op.f('ix_posts_slug'), 'posts', ['slug'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_posts_slug'), table_name='posts')
    op.drop_column('posts', 'slug')
