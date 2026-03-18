"""API key management endpoints."""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.db import ApiKey
from app.models.schemas import ApiKeyListItem, ApiKeyResponse, CreateApiKeyRequest

router = APIRouter(prefix="/keys", tags=["keys"])


@router.post("", response_model=ApiKeyResponse, status_code=201)
async def create_api_key(
    request: CreateApiKeyRequest,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ApiKeyResponse:
    """
    Generate a new API key for the authenticated user.
    The raw key is shown ONCE — store it safely.
    """
    raw_key = f"cb_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12]

    db_key = ApiKey(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=request.name,
        tier="free",
        daily_limit=100,
        monthly_limit=3000,
    )
    session.add(db_key)
    await session.commit()

    return ApiKeyResponse(
        key=raw_key,
        key_prefix=key_prefix,
        tier="free",
        daily_limit=100,
        created_at=datetime.now(timezone.utc),
    )


@router.get("", response_model=list[ApiKeyListItem])
async def list_api_keys(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[ApiKeyListItem]:
    """List all API keys for the authenticated user."""
    result = await session.execute(
        select(ApiKey)
        .where(ApiKey.user_id == uuid.UUID(user_id))
        .order_by(ApiKey.created_at.desc())
    )
    keys = result.scalars().all()
    return [
        ApiKeyListItem(
            id=str(k.id),
            key_prefix=k.key_prefix,
            name=k.name,
            tier=k.tier,
            daily_limit=k.daily_limit,
            is_active=k.is_active,
            last_used_at=k.last_used_at,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.delete("/{key_id}", status_code=204, response_model=None)
async def revoke_api_key(
    key_id: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Revoke (soft-delete) an API key by ID."""
    result = await session.execute(
        select(ApiKey).where(
            ApiKey.id == uuid.UUID(key_id),
            ApiKey.user_id == uuid.UUID(user_id),
        )
    )
    key = result.scalar_one_or_none()
    if key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = False
    await session.commit()
