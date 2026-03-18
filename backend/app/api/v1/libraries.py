"""Library search and resolution endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.models.schemas import (
    LibraryListResponse,
    ResolveLibraryRequest,
    ResolveLibraryResponse,
)
from app.services.library_service import LibraryService
from app.dependencies import get_library_service, verify_api_key

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.get("", response_model=LibraryListResponse)
async def list_libraries(
    category: str | None = Query(None, description="Filter by category"),
    q: str | None = Query(None, description="Search by name or description"),
    limit: int = Query(50, ge=1, le=200),
    service: LibraryService = Depends(get_library_service),
) -> LibraryListResponse:
    """List all indexed libraries, optionally filtered by category or search query."""
    libraries = await service.list(category=category, query=q, limit=limit)
    return LibraryListResponse(
        libraries=libraries,
        total=len(libraries),
        category=category,
    )


@router.post("/resolve", response_model=ResolveLibraryResponse)
async def resolve_library(
    request: ResolveLibraryRequest,
    _: str = Depends(verify_api_key),
    service: LibraryService = Depends(get_library_service),
) -> ResolveLibraryResponse:
    """
    Resolve a library name to a canonical Context7India library ID.
    This is the backend for the MCP resolve-library-id tool.

    Example: "razorpay" → "/razorpay/razorpay-sdk"
    """
    result = await service.resolve(
        query=request.query,
        library_name=request.library_name,
    )
    return result
