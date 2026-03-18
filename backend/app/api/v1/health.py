"""Health check endpoint — used by Railway liveness probes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Live health check with real DB and Redis connectivity tests."""
    db_ok = False
    redis_ok = False
    library_count = 0

    # Check DB
    try:
        result = await session.execute(text("SELECT COUNT(*) FROM libraries WHERE is_active = true"))
        library_count = result.scalar() or 0
        db_ok = True
    except Exception:
        pass

    # Check Redis
    try:
        from app.core.redis_client import get_cached
        await get_cached("health_check")
        redis_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        version="0.1.0",
        libraries_indexed=library_count,
        db_connected=db_ok,
        redis_connected=redis_ok,
    )
