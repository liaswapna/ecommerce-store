"""add product embedding

Revision ID: 7c2a9e41b3d5
Revises: 4e6066f2fb5a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = "7c2a9e41b3d5"
down_revision: Union[str, Sequence[str], None] = "4e6066f2fb5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("products", sa.Column("embedding", Vector(768), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "embedding")
