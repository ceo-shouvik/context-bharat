"""
Admin panel API endpoints.

All endpoints require INTERNAL_API_KEY authentication via Bearer token.
Provides dashboard stats, library management, ingestion monitoring,
error tracking, feature flag control, user/key management, analytics,
and system health checks.
"""
from __future__ import annotations

import logging
import platform
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.feature_flags import _flag_overrides, flags
from app.models.db import ApiKey, DocChunk, IngestionRun, Library

logger = logging.getLogger(__name__)

# ─── Server start time (for uptime calculation) ─────────────────────────────
_server_start_time = time.time()

# ─── Auth ────────────────────────────────────────────────────────────────────

_admin_security = HTTPBearer(auto_error=False)


async def verify_admin(
    credentials: HTTPAuthorizationCredentials | None = Security(_admin_security),
) -> str:
    """
    Verify that the request carries a valid admin Bearer token.

    Compares the Authorization header against ``settings.INTERNAL_API_KEY``.
    Returns the token string on success; raises 403 otherwise.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin authentication required.",
        )

    if not settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTERNAL_API_KEY is not configured on the server.",
        )

    if credentials.credentials != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key.",
        )

    return credentials.credentials


# ─── Router ──────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verify_admin)])


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Schemas
# ═══════════════════════════════════════════════════════════════════════════════


# --- Dashboard Stats ---

class DashboardStatsResponse(BaseModel):
    total_libraries: int
    active_libraries: int
    total_chunks: int
    total_api_keys: int
    total_ingestion_runs: int
    failed_runs_last_24h: int
    avg_freshness_score: float | None
    db_size_mb: float | None
    redis_connected: bool
    uptime_seconds: float


# --- Library Management ---

class AdminLibraryItem(BaseModel):
    id: str
    library_id: str
    name: str
    description: str | None = None
    category: str
    tags: list[str] = []
    npm_package: str | None = None
    pypi_package: str | None = None
    github_repo: str | None = None
    last_indexed_at: datetime | None = None
    freshness_score: float | None = None
    chunk_count: int = 0
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LibraryToggleResponse(BaseModel):
    library_id: str
    is_active: bool
    previous_value: bool


class LibraryReindexResponse(BaseModel):
    library_id: str
    message: str
    ingestion_run_id: str | None = None


class LibraryDeleteResponse(BaseModel):
    library_id: str
    message: str


# --- Ingestion Monitor ---

class IngestionRunItem(BaseModel):
    id: str
    library_id: str
    status: str
    chunks_indexed: int | None = None
    chunks_deleted: int | None = None
    errors: list[Any] = []
    triggered_by: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = None
    embedding_cost_usd: float | None = None


# --- Error / Ticket ---

class ErrorItem(BaseModel):
    run_id: str
    library_id: str
    status: str
    errors: list[Any]
    started_at: datetime | None = None
    completed_at: datetime | None = None


class CreateTicketRequest(BaseModel):
    platform: str = Field(..., pattern="^(github|jira)$", description="github or jira")
    title: str | None = None
    assignee: str | None = None


class CreateTicketResponse(BaseModel):
    ticket_url: str
    ticket_id: str
    platform: str


# --- Feature Flags ---

class FlagStateResponse(BaseModel):
    flags: dict[str, bool]
    overrides: dict[str, bool]


class SetFlagRequest(BaseModel):
    enabled: bool


class SetFlagResponse(BaseModel):
    flag_name: str
    enabled: bool
    previous_value: bool


# --- Users & Keys ---

class AdminUserItem(BaseModel):
    user_id: str
    key_count: int
    active_key_count: int
    tiers: list[str]


class AdminKeyItem(BaseModel):
    id: str
    user_id: str | None = None
    key_prefix: str
    name: str | None = None
    tier: str
    daily_limit: int
    monthly_limit: int
    is_active: bool
    last_used_at: datetime | None = None
    created_at: datetime | None = None


class RevokeKeyResponse(BaseModel):
    key_id: str
    revoked: bool


class ChangeTierRequest(BaseModel):
    tier: str = Field(..., pattern="^(free|pro|team)$")
    daily_limit: int = Field(..., gt=0)


class ChangeTierResponse(BaseModel):
    key_id: str
    tier: str
    daily_limit: int
    previous_tier: str
    previous_daily_limit: int


# --- Analytics ---

class DailyQueryVolume(BaseModel):
    date: str
    count: int


class PopularLibrary(BaseModel):
    library_id: str
    name: str
    query_count: int


class LanguageBreakdown(BaseModel):
    language: str
    count: int
    percentage: float


# --- System Health ---

class DatabaseHealth(BaseModel):
    connected: bool
    table_counts: dict[str, int]
    version: str | None = None


class RedisHealth(BaseModel):
    connected: bool
    memory_used: str | None = None
    keys_count: int | None = None


class SystemHealth(BaseModel):
    python_version: str
    fastapi_version: str
    uptime: float


class DetailedHealthResponse(BaseModel):
    database: DatabaseHealth
    redis: RedisHealth
    feature_flags: dict[str, Any]
    mcp_server: dict[str, Any]
    system: SystemHealth


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Dashboard Stats
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_db),
) -> DashboardStatsResponse:
    """Return high-level dashboard statistics from real database tables."""
    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(hours=24)

    total_libraries = (await session.execute(select(func.count(Library.id)))).scalar_one()
    active_libraries = (
        await session.execute(
            select(func.count(Library.id)).where(Library.is_active.is_(True))
        )
    ).scalar_one()
    total_chunks = (await session.execute(select(func.count(DocChunk.id)))).scalar_one()
    total_api_keys = (await session.execute(select(func.count(ApiKey.id)))).scalar_one()
    total_ingestion_runs = (
        await session.execute(select(func.count(IngestionRun.id)))
    ).scalar_one()
    failed_runs_last_24h = (
        await session.execute(
            select(func.count(IngestionRun.id)).where(
                IngestionRun.status == "failed",
                IngestionRun.started_at >= twenty_four_hours_ago,
            )
        )
    ).scalar_one()
    avg_freshness = (
        await session.execute(
            select(func.avg(Library.freshness_score)).where(
                Library.freshness_score.isnot(None)
            )
        )
    ).scalar_one()

    # Database size (Postgres-specific)
    db_size_mb: float | None = None
    try:
        row = await session.execute(
            text("SELECT pg_database_size(current_database()) / (1024*1024.0)")
        )
        db_size_mb = round(row.scalar_one(), 2)
    except Exception:
        logger.debug("Could not determine database size")

    # Redis connectivity check
    redis_connected = False
    try:
        from app.core.redis_client import _get_client

        client = _get_client()
        if client is not None:
            client.ping()
            redis_connected = True
    except Exception:
        pass

    return DashboardStatsResponse(
        total_libraries=total_libraries,
        active_libraries=active_libraries,
        total_chunks=total_chunks,
        total_api_keys=total_api_keys,
        total_ingestion_runs=total_ingestion_runs,
        failed_runs_last_24h=failed_runs_last_24h,
        avg_freshness_score=round(avg_freshness, 4) if avg_freshness is not None else None,
        db_size_mb=db_size_mb,
        redis_connected=redis_connected,
        uptime_seconds=round(time.time() - _server_start_time, 2),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Library Management
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/libraries", response_model=list[AdminLibraryItem])
async def list_all_libraries(
    session: AsyncSession = Depends(get_db),
) -> list[AdminLibraryItem]:
    """List all libraries with full metadata."""
    result = await session.execute(select(Library).order_by(Library.created_at.desc()))
    libraries = result.scalars().all()
    return [
        AdminLibraryItem(
            id=str(lib.id),
            library_id=lib.library_id,
            name=lib.name,
            description=lib.description,
            category=lib.category,
            tags=lib.tags or [],
            npm_package=lib.npm_package,
            pypi_package=lib.pypi_package,
            github_repo=lib.github_repo,
            last_indexed_at=lib.last_indexed_at,
            freshness_score=lib.freshness_score,
            chunk_count=lib.chunk_count,
            is_active=lib.is_active,
            created_at=lib.created_at,
            updated_at=lib.updated_at,
        )
        for lib in libraries
    ]


@router.post("/libraries/{library_id:path}/toggle", response_model=LibraryToggleResponse)
async def toggle_library(
    library_id: str,
    session: AsyncSession = Depends(get_db),
) -> LibraryToggleResponse:
    """Enable or disable a library."""
    result = await session.execute(
        select(Library).where(Library.library_id == library_id)
    )
    lib = result.scalar_one_or_none()
    if lib is None:
        raise HTTPException(status_code=404, detail=f"Library '{library_id}' not found")

    previous = lib.is_active
    lib.is_active = not previous
    await session.commit()

    logger.info("Library toggled", extra={"library_id": library_id, "is_active": lib.is_active})
    return LibraryToggleResponse(
        library_id=library_id, is_active=lib.is_active, previous_value=previous
    )


@router.post("/libraries/{library_id:path}/reindex", response_model=LibraryReindexResponse)
async def reindex_library(
    library_id: str,
    session: AsyncSession = Depends(get_db),
) -> LibraryReindexResponse:
    """Trigger re-indexing by creating a pending ingestion run for the next cron cycle."""
    result = await session.execute(
        select(Library).where(Library.library_id == library_id)
    )
    lib = result.scalar_one_or_none()
    if lib is None:
        raise HTTPException(status_code=404, detail=f"Library '{library_id}' not found")

    run = IngestionRun(
        id=uuid.uuid4(),
        library_id=library_id,
        status="pending",
        triggered_by="manual",
        started_at=datetime.now(timezone.utc),
    )
    session.add(run)
    await session.commit()

    logger.info("Reindex requested", extra={"library_id": library_id, "run_id": str(run.id)})
    return LibraryReindexResponse(
        library_id=library_id,
        message="Re-indexing queued. Will be picked up by the next cron cycle.",
        ingestion_run_id=str(run.id),
    )


@router.delete("/libraries/{library_id:path}", response_model=LibraryDeleteResponse)
async def delete_library(
    library_id: str,
    session: AsyncSession = Depends(get_db),
) -> LibraryDeleteResponse:
    """Soft-delete a library by marking it inactive."""
    result = await session.execute(
        select(Library).where(Library.library_id == library_id)
    )
    lib = result.scalar_one_or_none()
    if lib is None:
        raise HTTPException(status_code=404, detail=f"Library '{library_id}' not found")

    lib.is_active = False
    await session.commit()

    logger.info("Library soft-deleted", extra={"library_id": library_id})
    return LibraryDeleteResponse(
        library_id=library_id,
        message="Library has been soft-deleted (is_active=False).",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Ingestion Monitor
# ═══════════════════════════════════════════════════════════════════════════════


def _run_to_item(run: IngestionRun) -> IngestionRunItem:
    return IngestionRunItem(
        id=str(run.id),
        library_id=run.library_id,
        status=run.status,
        chunks_indexed=run.chunks_indexed,
        chunks_deleted=run.chunks_deleted,
        errors=run.errors or [],
        triggered_by=run.triggered_by,
        started_at=run.started_at,
        completed_at=run.completed_at,
        duration_seconds=run.duration_seconds,
        embedding_cost_usd=run.embedding_cost_usd,
    )


@router.get("/ingestion/runs", response_model=list[IngestionRunItem])
async def list_ingestion_runs(
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
) -> list[IngestionRunItem]:
    """List recent ingestion runs (most recent first)."""
    result = await session.execute(
        select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit)
    )
    return [_run_to_item(run) for run in result.scalars().all()]


@router.get("/ingestion/runs/{run_id}", response_model=IngestionRunItem)
async def get_ingestion_run(
    run_id: str,
    session: AsyncSession = Depends(get_db),
) -> IngestionRunItem:
    """Get details of a specific ingestion run."""
    result = await session.execute(
        select(IngestionRun).where(IngestionRun.id == uuid.UUID(run_id))
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail=f"Ingestion run '{run_id}' not found")
    return _run_to_item(run)


@router.get("/ingestion/errors", response_model=list[IngestionRunItem])
async def list_ingestion_errors(
    session: AsyncSession = Depends(get_db),
) -> list[IngestionRunItem]:
    """List all ingestion runs with errors in the last 7 days."""
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    result = await session.execute(
        select(IngestionRun)
        .where(
            IngestionRun.status == "failed",
            IngestionRun.started_at >= seven_days_ago,
        )
        .order_by(IngestionRun.started_at.desc())
    )
    return [_run_to_item(run) for run in result.scalars().all()]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Error Log -> Ticket Automation
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/errors/recent", response_model=list[ErrorItem])
async def get_recent_errors(
    session: AsyncSession = Depends(get_db),
) -> list[ErrorItem]:
    """Get all ingestion runs with errors from the last 24 hours."""
    twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    result = await session.execute(
        select(IngestionRun)
        .where(
            IngestionRun.status == "failed",
            IngestionRun.started_at >= twenty_four_hours_ago,
        )
        .order_by(IngestionRun.started_at.desc())
    )
    return [
        ErrorItem(
            run_id=str(run.id),
            library_id=run.library_id,
            status=run.status,
            errors=run.errors or [],
            started_at=run.started_at,
            completed_at=run.completed_at,
        )
        for run in result.scalars().all()
    ]


@router.post("/errors/{error_id}/create-ticket", response_model=CreateTicketResponse)
async def create_ticket_from_error(
    error_id: str,
    request: CreateTicketRequest,
    session: AsyncSession = Depends(get_db),
) -> CreateTicketResponse:
    """
    Create a GitHub issue or Jira ticket from an ingestion error.

    For MVP this formats the ticket data and returns it without making an
    actual external API call (tokens are not yet configured).
    """
    result = await session.execute(
        select(IngestionRun).where(IngestionRun.id == uuid.UUID(error_id))
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail=f"Ingestion run '{error_id}' not found")

    title = request.title or f"Ingestion failure: {run.library_id} ({run.status})"
    ticket_id = f"CB-{uuid.uuid4().hex[:8].upper()}"

    if request.platform == "github":
        ticket_url = f"https://github.com/contextbharat/context-bharat/issues/new?title={title}"
    else:
        ticket_url = f"https://jira.example.com/browse/{ticket_id}"

    logger.info(
        "Ticket created (MVP stub)",
        extra={"ticket_id": ticket_id, "platform": request.platform, "error_id": error_id},
    )
    return CreateTicketResponse(
        ticket_url=ticket_url,
        ticket_id=ticket_id,
        platform=request.platform,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Feature Flag Control
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/flags", response_model=FlagStateResponse)
async def get_feature_flags() -> FlagStateResponse:
    """Get all current feature flag states including any runtime overrides."""
    return FlagStateResponse(
        flags=flags.to_dict(),
        overrides=dict(_flag_overrides),
    )


@router.post("/flags/{flag_name}", response_model=SetFlagResponse)
async def set_feature_flag(
    flag_name: str,
    request: SetFlagRequest,
) -> SetFlagResponse:
    """Toggle a feature flag at runtime (override persists until server restart)."""
    all_flags = flags.to_dict()
    if flag_name not in all_flags:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown flag '{flag_name}'. Available: {list(all_flags.keys())}",
        )

    previous_value = all_flags[flag_name]
    _flag_overrides[flag_name] = request.enabled

    logger.info(
        "Feature flag toggled",
        extra={"flag": flag_name, "enabled": request.enabled, "previous": previous_value},
    )
    return SetFlagResponse(
        flag_name=flag_name,
        enabled=request.enabled,
        previous_value=previous_value,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. User & API Key Management
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/users", response_model=list[AdminUserItem])
async def list_users(
    session: AsyncSession = Depends(get_db),
) -> list[AdminUserItem]:
    """List users with their key count and usage summary."""
    result = await session.execute(
        select(
            ApiKey.user_id,
            func.count(ApiKey.id).label("key_count"),
            func.count(ApiKey.id).filter(ApiKey.is_active.is_(True)).label("active_key_count"),
            func.array_agg(func.distinct(ApiKey.tier)).label("tiers"),
        )
        .where(ApiKey.user_id.isnot(None))
        .group_by(ApiKey.user_id)
    )
    rows = result.all()
    return [
        AdminUserItem(
            user_id=str(row.user_id),
            key_count=row.key_count,
            active_key_count=row.active_key_count,
            tiers=row.tiers or [],
        )
        for row in rows
    ]


@router.get("/keys", response_model=list[AdminKeyItem])
async def list_all_keys(
    session: AsyncSession = Depends(get_db),
) -> list[AdminKeyItem]:
    """List all API keys with usage stats."""
    result = await session.execute(select(ApiKey).order_by(ApiKey.created_at.desc()))
    keys = result.scalars().all()
    return [
        AdminKeyItem(
            id=str(k.id),
            user_id=str(k.user_id) if k.user_id else None,
            key_prefix=k.key_prefix,
            name=k.name,
            tier=k.tier,
            daily_limit=k.daily_limit,
            monthly_limit=k.monthly_limit,
            is_active=k.is_active,
            last_used_at=k.last_used_at,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.post("/keys/{key_id}/revoke", response_model=RevokeKeyResponse)
async def admin_revoke_key(
    key_id: str,
    session: AsyncSession = Depends(get_db),
) -> RevokeKeyResponse:
    """Admin-revoke an API key by ID (sets is_active=False)."""
    result = await session.execute(
        select(ApiKey).where(ApiKey.id == uuid.UUID(key_id))
    )
    key = result.scalar_one_or_none()
    if key is None:
        raise HTTPException(status_code=404, detail=f"API key '{key_id}' not found")

    key.is_active = False
    await session.commit()

    logger.info("Admin revoked API key", extra={"key_id": key_id})
    return RevokeKeyResponse(key_id=key_id, revoked=True)


@router.post("/keys/{key_id}/change-tier", response_model=ChangeTierResponse)
async def change_key_tier(
    key_id: str,
    request: ChangeTierRequest,
    session: AsyncSession = Depends(get_db),
) -> ChangeTierResponse:
    """Change the tier and daily limit of an API key."""
    result = await session.execute(
        select(ApiKey).where(ApiKey.id == uuid.UUID(key_id))
    )
    key = result.scalar_one_or_none()
    if key is None:
        raise HTTPException(status_code=404, detail=f"API key '{key_id}' not found")

    previous_tier = key.tier
    previous_daily_limit = key.daily_limit

    key.tier = request.tier
    key.daily_limit = request.daily_limit
    await session.commit()

    logger.info(
        "API key tier changed",
        extra={
            "key_id": key_id,
            "tier": request.tier,
            "daily_limit": request.daily_limit,
            "previous_tier": previous_tier,
        },
    )
    return ChangeTierResponse(
        key_id=key_id,
        tier=request.tier,
        daily_limit=request.daily_limit,
        previous_tier=previous_tier,
        previous_daily_limit=previous_daily_limit,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Analytics (MVP — sample data where real data is unavailable)
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/analytics/queries", response_model=list[DailyQueryVolume])
async def get_query_analytics() -> list[DailyQueryVolume]:
    """
    Query volume by day for the last 30 days.

    MVP: returns realistic sample data since there is no query_logs table yet.
    """
    import random

    today = datetime.now(timezone.utc).date()
    return [
        DailyQueryVolume(
            date=(today - timedelta(days=i)).isoformat(),
            count=random.randint(80, 500),
        )
        for i in range(30)
    ]


@router.get("/analytics/popular-libraries", response_model=list[PopularLibrary])
async def get_popular_libraries(
    session: AsyncSession = Depends(get_db),
) -> list[PopularLibrary]:
    """
    Most queried libraries.

    MVP: returns top libraries by chunk_count as a proxy for popularity.
    """
    result = await session.execute(
        select(Library)
        .where(Library.is_active.is_(True))
        .order_by(Library.chunk_count.desc())
        .limit(20)
    )
    libraries = result.scalars().all()
    return [
        PopularLibrary(
            library_id=lib.library_id,
            name=lib.name,
            query_count=lib.chunk_count * 3,  # estimated proxy
        )
        for lib in libraries
    ]


@router.get("/analytics/languages", response_model=list[LanguageBreakdown])
async def get_language_analytics(
    session: AsyncSession = Depends(get_db),
) -> list[LanguageBreakdown]:
    """
    Query breakdown by language.

    MVP: uses actual doc_chunk language distribution as a proxy.
    """
    result = await session.execute(
        select(DocChunk.language, func.count(DocChunk.id).label("cnt"))
        .group_by(DocChunk.language)
    )
    rows = result.all()
    total = sum(row.cnt for row in rows) or 1
    return [
        LanguageBreakdown(
            language=row.language or "en",
            count=row.cnt,
            percentage=round(row.cnt / total * 100, 2),
        )
        for row in rows
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# 8. System Health
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def get_detailed_health(
    session: AsyncSession = Depends(get_db),
) -> DetailedHealthResponse:
    """Comprehensive health check covering database, Redis, flags, and system."""

    # ── Database ──
    db_connected = True
    table_counts: dict[str, int] = {}
    db_version: str | None = None
    try:
        table_counts["libraries"] = (
            await session.execute(select(func.count(Library.id)))
        ).scalar_one()
        table_counts["doc_chunks"] = (
            await session.execute(select(func.count(DocChunk.id)))
        ).scalar_one()
        table_counts["api_keys"] = (
            await session.execute(select(func.count(ApiKey.id)))
        ).scalar_one()
        table_counts["ingestion_runs"] = (
            await session.execute(select(func.count(IngestionRun.id)))
        ).scalar_one()

        version_row = await session.execute(text("SELECT version()"))
        db_version = version_row.scalar_one()
    except Exception as exc:
        db_connected = False
        logger.warning("Database health check failed", exc_info=exc)

    # ── Redis ──
    redis_connected = False
    redis_memory: str | None = None
    redis_keys: int | None = None
    try:
        from app.core.redis_client import _get_client

        client = _get_client()
        if client is not None:
            client.ping()
            redis_connected = True
            # Attempt to get info (may not be available on all Redis providers)
            try:
                info = client.info()
                if isinstance(info, dict):
                    redis_memory = info.get("used_memory_human")
                    redis_keys = info.get("db0", {}).get("keys") if isinstance(info.get("db0"), dict) else None
            except Exception:
                pass
    except Exception:
        pass

    # ── Feature Flags ──
    flags_dict = flags.to_dict()
    enabled_count = sum(1 for v in flags_dict.values() if v)
    disabled_count = len(flags_dict) - enabled_count

    # ── FastAPI version ──
    try:
        import fastapi

        fastapi_version = fastapi.__version__
    except Exception:
        fastapi_version = "unknown"

    return DetailedHealthResponse(
        database=DatabaseHealth(
            connected=db_connected,
            table_counts=table_counts,
            version=db_version,
        ),
        redis=RedisHealth(
            connected=redis_connected,
            memory_used=redis_memory,
            keys_count=redis_keys,
        ),
        feature_flags={
            "enabled_count": enabled_count,
            "disabled_count": disabled_count,
            "flags": flags_dict,
        },
        mcp_server={
            "version": "0.1.0",
            "status": "configured",
        },
        system=SystemHealth(
            python_version=platform.python_version(),
            fastapi_version=fastapi_version,
            uptime=round(time.time() - _server_start_time, 2),
        ),
    )
