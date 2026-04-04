"""SQLAlchemy database models."""
from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Library(Base):
    """An indexed documentation library (API, SDK, framework, government spec)."""
    __tablename__ = "libraries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    npm_package: Mapped[str | None] = mapped_column(String(255))
    pypi_package: Mapped[str | None] = mapped_column(String(255))
    github_repo: Mapped[str | None] = mapped_column(String(255))
    last_indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    freshness_score: Mapped[float | None] = mapped_column(Float)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class DocChunk(Base):
    """A 512-token documentation chunk with vector embedding."""
    __tablename__ = "doc_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id: Mapped[str] = mapped_column(String(255), ForeignKey("libraries.library_id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384))  # BAAI/bge-small-en-v1.5
    url: Mapped[str | None] = mapped_column(Text)
    section: Mapped[str | None] = mapped_column(String(500))
    language: Mapped[str] = mapped_column(String(10), default="en", index=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)  # SHA256
    chunk_metadata: Mapped[dict] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class ApiKey(Base):
    """API key for authenticating MCP server and direct API requests."""
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)  # SHA256
    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)  # First 8 chars for display
    name: Mapped[str | None] = mapped_column(String(255))
    tier: Mapped[str] = mapped_column(String(20), default="free")  # free | pro | team
    daily_limit: Mapped[int] = mapped_column(Integer, default=100)
    monthly_limit: Mapped[int] = mapped_column(Integer, default=3000)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IngestionRun(Base):
    """Audit log for ingestion pipeline runs."""
    __tablename__ = "ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # pending | running | success | failed
    chunks_indexed: Mapped[int | None] = mapped_column(Integer)
    chunks_deleted: Mapped[int | None] = mapped_column(Integer)
    errors: Mapped[list] = mapped_column(JSONB, default=[])
    triggered_by: Mapped[str | None] = mapped_column(String(50))  # cron | version_bump | manual | pr
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    embedding_cost_usd: Mapped[float | None] = mapped_column(Float)
