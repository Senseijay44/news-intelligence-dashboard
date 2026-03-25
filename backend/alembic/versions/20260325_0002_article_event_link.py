"""add article event link

Revision ID: 20260325_0002
Revises: 20260325_0001
Create Date: 2026-03-25 01:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260325_0002"
down_revision = "20260325_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("article", sa.Column("event_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_article_event_id"), "article", ["event_id"], unique=False)
    op.create_foreign_key("fk_article_event_id_event", "article", "event", ["event_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_article_event_id_event", "article", type_="foreignkey")
    op.drop_index(op.f("ix_article_event_id"), table_name="article")
    op.drop_column("article", "event_id")
