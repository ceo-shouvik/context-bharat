"""Feature flags endpoint — returns current feature flag states."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.feature_flags import flags

router = APIRouter(prefix="/features", tags=["features"])


@router.get("")
async def get_feature_flags() -> dict:
    """Return all feature flag states. Useful for frontend to show/hide features."""
    return {"features": flags.to_dict()}
