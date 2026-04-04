"""Switch embedding dimensions from 1536 (OpenAI) to 384 (fastembed/bge-small).

Revision ID: 002
Revises: 001
Create Date: 2026-04-04
"""
from __future__ import annotations

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old IVFFlat index (dimension-specific)
    op.execute("DROP INDEX IF EXISTS idx_doc_chunks_embedding")
    # Alter column from vector(1536) to vector(384)
    op.execute("ALTER TABLE doc_chunks ALTER COLUMN embedding TYPE vector(384)")
    # Recreate IVFFlat index with new dimensions
    op.execute("""
        CREATE INDEX idx_doc_chunks_embedding ON doc_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_doc_chunks_embedding")
    op.execute("ALTER TABLE doc_chunks ALTER COLUMN embedding TYPE vector(1536)")
    op.execute("""
        CREATE INDEX idx_doc_chunks_embedding ON doc_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)
