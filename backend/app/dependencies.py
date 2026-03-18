"""FastAPI dependency injection — DB sessions, auth, service instances."""
from __future__ import annotations

import hashlib
import logging

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import check_rate_limit

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    session: AsyncSession = Depends(get_db),
) -> str:
    """
    Verify API key from Authorization Bearer header.
    - No key: apply anonymous free-tier limits
    - Valid key: return key prefix, enforce tier limits
    - Invalid key: 401
    """
    if credentials is None:
        # Anonymous — free tier (100 queries/day by IP is handled at nginx/CF level)
        return "anonymous"

    raw_key = credentials.credentials

    # Validate format
    if not raw_key.startswith("c7i_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. Keys start with 'c7i_'.",
        )

    # Hash and look up in DB
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12]

    from sqlalchemy import select
    from app.models.db import ApiKey

    result = await session.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    )
    api_key = result.scalar_one_or_none()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not found or revoked.",
        )

    # Rate limit check
    is_allowed, current_count = await check_rate_limit(key_prefix, api_key.daily_limit)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit of {api_key.daily_limit} queries reached. Upgrade to Pro for unlimited access.",
            headers={"X-RateLimit-Limit": str(api_key.daily_limit), "X-RateLimit-Used": str(current_count)},
        )

    # Update last_used_at (async, non-blocking)
    from datetime import datetime, timezone
    try:
        api_key.last_used_at = datetime.now(timezone.utc)
        await session.commit()
    except Exception:
        pass  # Non-critical

    return key_prefix


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> str:
    """
    Validate Supabase JWT and return user_id.
    Used by authenticated endpoints (key management, dashboard).
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    token = credentials.credentials

    try:
        from jose import JWTError, jwt
        from app.core.config import settings

        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )


def get_library_service():
    """Inject LibraryService (stateless — no session needed, creates own)."""
    from app.services.library_service import LibraryService
    return LibraryService()


def get_search_service():
    """Inject SearchService (stateless — creates own sessions)."""
    from app.services.search_service import SearchService
    return SearchService()
