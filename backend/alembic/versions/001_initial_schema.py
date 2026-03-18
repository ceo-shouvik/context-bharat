"""Initial schema — libraries, doc_chunks, api_keys, ingestion_runs.

Revision ID: 001
Revises:
Create Date: 2026-03-18
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "libraries",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("library_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("tags", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("npm_package", sa.String(255), nullable=True),
        sa.Column("pypi_package", sa.String(255), nullable=True),
        sa.Column("github_repo", sa.String(255), nullable=True),
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("freshness_score", sa.Float(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("library_id"),
    )
    op.create_index("idx_libraries_category", "libraries", ["category"])
    op.create_index("idx_libraries_library_id", "libraries", ["library_id"])

    op.create_table(
        "doc_chunks",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("library_id", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("section", sa.String(500), nullable=True),
        sa.Column("language", sa.String(10), server_default="en"),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("chunk_metadata", sa.JSON(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["library_id"], ["libraries.library_id"]),
    )
    op.create_index("idx_doc_chunks_library_id", "doc_chunks", ["library_id"])
    op.create_index("idx_doc_chunks_language", "doc_chunks", ["language"])
    op.create_index("idx_doc_chunks_content_hash", "doc_chunks", ["content_hash"])
    # pgvector IVFFlat index
    op.execute("""
        CREATE INDEX idx_doc_chunks_embedding ON doc_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    op.create_table(
        "api_keys",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("key_prefix", sa.String(12), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("tier", sa.String(20), server_default="free"),
        sa.Column("daily_limit", sa.Integer(), server_default="100"),
        sa.Column("monthly_limit", sa.Integer(), server_default="3000"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("library_id", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("chunks_indexed", sa.Integer(), nullable=True),
        sa.Column("chunks_deleted", sa.Integer(), nullable=True),
        sa.Column("errors", sa.JSON(), server_default="[]"),
        sa.Column("triggered_by", sa.String(50), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("embedding_cost_usd", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ingestion_runs_library_id", "ingestion_runs", ["library_id"])


def downgrade() -> None:
    op.drop_table("ingestion_runs")
    op.drop_table("api_keys")
    op.drop_table("doc_chunks")
    op.drop_table("libraries")
