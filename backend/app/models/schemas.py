"""Pydantic request/response schemas for the REST API."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class Language(str, Enum):
    EN = "en"
    HI = "hi"
    TA = "ta"
    TE = "te"
    KN = "kn"
    BN = "bn"


class LibraryCategory(str, Enum):
    INDIAN_FINTECH = "indian-fintech"
    INDIA_DPI = "india-dpi"
    INDIAN_TRADING = "indian-trading"
    ENTERPRISE_INDIA = "enterprise-india"
    INDIAN_AI = "indian-ai"
    GLOBAL_FRAMEWORK = "global-framework"
    SAAS_CLOUD = "saas-cloud"


# ─── Library Schemas ──────────────────────────────────────────────────────────

class LibraryResult(BaseModel):
    library_id: str = Field(..., description="Canonical library ID, e.g. /razorpay/razorpay-sdk")
    name: str
    description: str | None = None
    category: str
    tags: list[str] = []
    freshness_score: float | None = None
    last_indexed_at: datetime | None = None
    chunk_count: int = 0


class ResolveLibraryRequest(BaseModel):
    query: str = Field(..., description="User's original query")
    library_name: str = Field(..., description="Extracted library name to resolve")


class ResolveLibraryResponse(BaseModel):
    library_id: str
    name: str
    description: str | None = None
    versions: list[str] = []
    tags: list[str] = []
    confidence: float = Field(..., description="Resolution confidence 0-1")


class LibraryListResponse(BaseModel):
    libraries: list[LibraryResult]
    total: int
    category: str | None = None


# ─── Docs / Query Schemas ─────────────────────────────────────────────────────

class QueryDocsRequest(BaseModel):
    library_id: str = Field(..., description="Context7India library ID")
    query: str = Field(..., description="Developer's question or task")
    token_budget: int = Field(default=5000, ge=100, le=20000)
    language: Language = Field(default=Language.EN)


class QueryDocsResponse(BaseModel):
    docs: str = Field(..., description="Relevant documentation as Markdown")
    library_id: str
    library_name: str
    sources: list[str] = Field(default=[], description="Source URLs")
    freshness_score: float | None = None
    language: str = "en"
    token_count: int = 0


# ─── API Key Schemas ──────────────────────────────────────────────────────────

class CreateApiKeyRequest(BaseModel):
    name: str | None = Field(None, description="Human-readable name for the key")


class ApiKeyResponse(BaseModel):
    key: str = Field(..., description="The API key — shown ONCE, store it safely")
    key_prefix: str = Field(..., description="First 8 chars for display purposes")
    tier: str
    daily_limit: int
    created_at: datetime


class ApiKeyListItem(BaseModel):
    id: str
    key_prefix: str
    name: str | None
    tier: str
    daily_limit: int
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime


# ─── Health Schema ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    libraries_indexed: int
    db_connected: bool
    redis_connected: bool
