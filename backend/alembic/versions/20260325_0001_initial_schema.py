"""initial schema

Revision ID: 20260325_0001
Revises:
Create Date: 2026-03-25 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260325_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("homepage", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_source_name"), "source", ["name"], unique=False)

    op.create_table(
        "event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("canonical_title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("location_name", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_event_canonical_title"), "event", ["canonical_title"], unique=False)
    op.create_index(op.f("ix_event_location_name"), "event", ["location_name"], unique=False)

    op.create_table(
        "geocodecache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("query", sa.String(), nullable=False),
        sa.Column("query_normalized", sa.String(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("query_normalized"),
    )
    op.create_index(op.f("ix_geocodecache_query_normalized"), "geocodecache", ["query_normalized"], unique=False)

    op.create_table(
        "article",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("location_name", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=False), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index(op.f("ix_article_location_name"), "article", ["location_name"], unique=False)
    op.create_index(op.f("ix_article_published_at"), "article", ["published_at"], unique=False)
    op.create_index(op.f("ix_article_title"), "article", ["title"], unique=False)
    op.create_index(op.f("ix_article_url"), "article", ["url"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_article_url"), table_name="article")
    op.drop_index(op.f("ix_article_title"), table_name="article")
    op.drop_index(op.f("ix_article_published_at"), table_name="article")
    op.drop_index(op.f("ix_article_location_name"), table_name="article")
    op.drop_table("article")

    op.drop_index(op.f("ix_geocodecache_query_normalized"), table_name="geocodecache")
    op.drop_table("geocodecache")

    op.drop_index(op.f("ix_event_location_name"), table_name="event")
    op.drop_index(op.f("ix_event_canonical_title"), table_name="event")
    op.drop_table("event")

    op.drop_index(op.f("ix_source_name"), table_name="source")
    op.drop_table("source")
