"""
Library service — metadata management, name resolution, fuzzy matching.

Resolve priority:
  1. Exact match on library_id
  2. Exact name match (case-insensitive)
  3. Fuzzy name match (Levenshtein distance)
  4. Tag match
  5. Semantic search on descriptions (embedding similarity)
"""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.db import Library
from app.models.schemas import LibraryResult, ResolveLibraryResponse
from app.repositories.library_repo import LibraryRepository

logger = logging.getLogger(__name__)

# Levenshtein threshold — names within this distance are "close enough"
FUZZY_DISTANCE_THRESHOLD = 5


class LibraryService:
    async def list(
        self,
        category: str | None = None,
        query: str | None = None,
        limit: int = 50,
    ) -> list[LibraryResult]:
        """List libraries with optional category and text filtering."""
        async with AsyncSessionLocal() as session:
            repo = LibraryRepository(session)
            libraries = await repo.search(query=query, category=category, limit=limit)
            return [_to_result(lib) for lib in libraries]

    async def resolve(
        self,
        query: str,
        library_name: str,
    ) -> ResolveLibraryResponse:
        """
        Resolve a library name to its canonical ID.
        Uses multi-stage resolution with confidence scoring.
        """
        async with AsyncSessionLocal() as session:
            repo = LibraryRepository(session)
            all_libs = await repo.search(limit=500)  # Load all for matching

        name_lower = library_name.lower().strip()

        # Stage 1: Exact library_id match
        for lib in all_libs:
            if lib.library_id.lower() == name_lower or lib.library_id.lstrip("/") == name_lower:
                return _to_resolve_response(lib, confidence=1.0)

        # Stage 2: Exact name match
        for lib in all_libs:
            if lib.name.lower() == name_lower:
                return _to_resolve_response(lib, confidence=0.98)

        # Stage 3: Name contains match (e.g. "kite" → "Zerodha Kite API")
        contains_matches = [
            lib for lib in all_libs
            if name_lower in lib.name.lower() or lib.name.lower() in name_lower
        ]
        if contains_matches:
            best = max(contains_matches, key=lambda l: _name_overlap(name_lower, l.name.lower()))
            return _to_resolve_response(best, confidence=0.90)

        # Stage 4: Tag match
        query_words = set(name_lower.split())
        tag_matches = [
            (lib, len(query_words & set(t.lower() for t in (lib.tags or []))))
            for lib in all_libs
        ]
        tag_matches = [(lib, score) for lib, score in tag_matches if score > 0]
        if tag_matches:
            best_lib, best_score = max(tag_matches, key=lambda x: x[1])
            return _to_resolve_response(best_lib, confidence=0.75)

        # Stage 5: Fuzzy name match (Levenshtein)
        try:
            from Levenshtein import distance as lev_distance
            scored = [
                (lib, lev_distance(name_lower, lib.name.lower()))
                for lib in all_libs
            ]
            scored.sort(key=lambda x: x[1])
            if scored and scored[0][1] <= FUZZY_DISTANCE_THRESHOLD:
                return _to_resolve_response(scored[0][0], confidence=0.60)
        except ImportError:
            # python-Levenshtein not installed — skip fuzzy match
            pass

        # Stage 6: Partial word match
        name_words = set(name_lower.split())
        word_matches = [
            (lib, len(name_words & set(lib.name.lower().split())))
            for lib in all_libs
        ]
        word_matches = [(lib, score) for lib, score in word_matches if score > 0]
        if word_matches:
            best_lib, best_score = max(word_matches, key=lambda x: x[1])
            return _to_resolve_response(best_lib, confidence=0.50)

        # Not found — return best guess with low confidence
        logger.warning(f"Could not resolve library: {library_name!r} (query: {query!r})")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Library '{library_name}' not found. Browse available libraries at context7india.com/libraries",
        )

    async def update_freshness(self, library_id: str, chunk_count: int) -> None:
        """Update freshness score and chunk count after ingestion."""
        from datetime import datetime, timezone
        async with AsyncSessionLocal() as session:
            repo = LibraryRepository(session)
            lib = await repo.get_by_id(library_id)
            if lib:
                lib.last_indexed_at = datetime.now(timezone.utc)
                lib.chunk_count = chunk_count
                lib.freshness_score = 1.0
                await session.commit()


def _name_overlap(a: str, b: str) -> float:
    """Score how much two names overlap (0-1)."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / max(len(words_a), len(words_b))


def _to_result(lib: Library) -> LibraryResult:
    return LibraryResult(
        library_id=lib.library_id,
        name=lib.name,
        description=lib.description,
        category=lib.category,
        tags=lib.tags or [],
        freshness_score=lib.freshness_score,
        last_indexed_at=lib.last_indexed_at,
        chunk_count=lib.chunk_count,
    )


def _to_resolve_response(lib: Library, confidence: float) -> ResolveLibraryResponse:
    versions = _extract_versions(lib)
    return ResolveLibraryResponse(
        library_id=lib.library_id,
        name=lib.name,
        description=lib.description,
        versions=versions,
        tags=lib.tags or [],
        confidence=confidence,
    )


def _extract_versions(lib: Library) -> list[str]:
    """Extract version info from library metadata. Best-effort, returns empty on failure."""
    import re
    versions: list[str] = []
    # Check description for version patterns (e.g., "v3", "v2.5", "API v1.3")
    if lib.description:
        found = re.findall(r"v(\d+(?:\.\d+)*)", lib.description, re.IGNORECASE)
        versions.extend(found)
    return sorted(set(versions), reverse=True)[:5]
