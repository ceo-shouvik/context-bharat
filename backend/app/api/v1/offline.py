"""Offline documentation packs — downloadable bundles of doc chunks per library."""
from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/offline", tags=["offline"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class OfflineChunk(BaseModel):
    content: str
    section: str | None = None
    url: str | None = None


class OfflinePackMeta(BaseModel):
    library_id: str
    name: str
    description: str | None = None
    total_chunks: int
    size_bytes: int
    category: str | None = None


class OfflinePackListResponse(BaseModel):
    packs: list[OfflinePackMeta]
    total: int


class OfflinePackResponse(BaseModel):
    library_id: str
    name: str
    chunks: list[OfflineChunk]
    total_chunks: int
    size_bytes: int


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/packs", response_model=OfflinePackListResponse)
async def list_offline_packs(
    session: AsyncSession = Depends(get_db),
) -> OfflinePackListResponse:
    """
    List all available offline documentation packs.

    Returns metadata about each library that has indexed doc chunks available
    for offline download.
    """
    if not flags.OFFLINE_PACKS:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    try:
        result = await session.execute(
            text("""
                SELECT
                    l.library_id,
                    l.name,
                    l.description,
                    l.category,
                    l.chunk_count,
                    COALESCE(SUM(LENGTH(dc.content)), 0) AS total_size
                FROM libraries l
                LEFT JOIN doc_chunks dc ON l.library_id = dc.library_id
                WHERE l.is_active = true AND l.chunk_count > 0
                GROUP BY l.library_id, l.name, l.description, l.category, l.chunk_count
                ORDER BY l.chunk_count DESC
            """)
        )
        rows = result.fetchall()

        packs = [
            OfflinePackMeta(
                library_id=row.library_id,
                name=row.name,
                description=row.description,
                total_chunks=row.chunk_count or 0,
                size_bytes=int(row.total_size or 0),
                category=row.category,
            )
            for row in rows
        ]

        return OfflinePackListResponse(packs=packs, total=len(packs))

    except Exception as e:
        logger.error("Failed to list offline packs", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list offline packs: {e}")


@router.get("/packs/{library_id:path}", response_model=OfflinePackResponse)
async def download_offline_pack(
    library_id: str,
    session: AsyncSession = Depends(get_db),
) -> OfflinePackResponse:
    """
    Download an offline documentation pack for a specific library.

    Returns all doc chunks for the library as a JSON bundle suitable for
    local caching and offline use.
    """
    if not flags.OFFLINE_PACKS:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    # Normalize library_id
    if not library_id.startswith("/"):
        library_id = f"/{library_id}"

    try:
        # Get library metadata
        lib_result = await session.execute(
            text("SELECT library_id, name FROM libraries WHERE library_id = :lid AND is_active = true"),
            {"lid": library_id},
        )
        library = lib_result.fetchone()

        if library is None:
            raise HTTPException(
                status_code=404,
                detail=f"Library {library_id!r} not found or not indexed.",
            )

        # Get all doc chunks
        chunks_result = await session.execute(
            text("""
                SELECT content, section, url
                FROM doc_chunks
                WHERE library_id = :lid AND language = 'en'
                ORDER BY section, created_at
            """),
            {"lid": library_id},
        )
        rows = chunks_result.fetchall()

        chunks = [
            OfflineChunk(
                content=row.content,
                section=row.section,
                url=row.url,
            )
            for row in rows
        ]

        total_size = sum(len(c.content.encode("utf-8")) for c in chunks)

        return OfflinePackResponse(
            library_id=library.library_id,
            name=library.name,
            chunks=chunks,
            total_chunks=len(chunks),
            size_bytes=total_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to build offline pack",
            extra={"library_id": library_id},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to build offline pack: {e}")
