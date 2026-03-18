"""Documentation query endpoint — the core MCP tool backend."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import QueryDocsRequest, QueryDocsResponse
from app.services.search_service import SearchService
from app.dependencies import get_search_service, verify_api_key

router = APIRouter(prefix="/docs", tags=["docs"])


@router.post("/query", response_model=QueryDocsResponse)
async def query_docs(
    request: QueryDocsRequest,
    _: str = Depends(verify_api_key),
    search_service: SearchService = Depends(get_search_service),
) -> QueryDocsResponse:
    """
    Retrieve relevant documentation for a library.
    This is the backend for the MCP query-docs tool.

    Returns Markdown-formatted documentation chunks within the token budget.
    """
    result = await search_service.query(
        library_id=request.library_id,
        query=request.query,
        token_budget=request.token_budget,
        language=request.language,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Library {request.library_id!r} not found or not indexed.",
        )

    return result
