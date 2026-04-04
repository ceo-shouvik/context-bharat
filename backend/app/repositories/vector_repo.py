"""Vector repository — pgvector similarity search."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import DocChunk


@dataclass
class SearchResult:
    chunk_id: str
    library_id: str
    content: str
    url: str | None
    section: str | None
    language: str
    score: float


class VectorRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def similarity_search(
        self,
        embedding: list[float],
        library_id: str,
        language: str = "en",
        limit: int = 20,
    ) -> list[SearchResult]:
        """Cosine similarity search using pgvector."""
        # pgvector cosine distance operator: <=>
        result = await self._session.execute(
            text("""
                SELECT id, library_id, content, url, section, language,
                       1 - (embedding <=> :embedding) AS score
                FROM doc_chunks
                WHERE library_id = :library_id AND language = :language
                ORDER BY embedding <=> :embedding
                LIMIT :limit
            """),
            {
                "embedding": str(embedding),
                "library_id": library_id,
                "language": language,
                "limit": limit,
            },
        )
        return [
            SearchResult(
                chunk_id=str(row.id),
                library_id=row.library_id,
                content=row.content,
                url=row.url,
                section=row.section,
                language=row.language,
                score=float(row.score) if row.score is not None else 0.0,
            )
            for row in result.fetchall()
        ]

    async def keyword_search(
        self,
        query: str,
        library_id: str,
        language: str = "en",
        limit: int = 20,
    ) -> list[SearchResult]:
        """BM25-style full-text search using PostgreSQL ts_rank."""
        result = await self._session.execute(
            text("""
                SELECT id, library_id, content, url, section, language,
                       ts_rank(to_tsvector('english', content),
                               plainto_tsquery('english', :query)) AS score
                FROM doc_chunks
                WHERE library_id = :library_id
                  AND language = :language
                  AND to_tsvector('english', content) @@ plainto_tsquery('english', :query)
                ORDER BY score DESC
                LIMIT :limit
            """),
            {"query": query, "library_id": library_id, "language": language, "limit": limit},
        )
        return [
            SearchResult(
                chunk_id=str(row.id),
                library_id=row.library_id,
                content=row.content,
                url=row.url,
                section=row.section,
                language=row.language,
                score=float(row.score) if row.score is not None else 0.0,
            )
            for row in result.fetchall()
        ]

    async def bulk_upsert(self, chunks: list[DocChunk]) -> int:
        """Insert or update chunks by content_hash."""
        existing_hashes = await self._get_existing_hashes(
            chunks[0].library_id if chunks else ""
        )
        inserted = 0
        for chunk in chunks:
            if chunk.content_hash in existing_hashes:
                # Update metadata only
                stmt = select(DocChunk).where(DocChunk.content_hash == chunk.content_hash)
                result = await self._session.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    existing.url = chunk.url
                    existing.section = chunk.section
                    existing.chunk_metadata = chunk.chunk_metadata
            else:
                self._session.add(chunk)
                inserted += 1
        await self._session.commit()
        return inserted

    async def delete_stale(self, library_id: str, current_hashes: set[str]) -> int:
        """Delete chunks no longer present in current crawl."""
        hashes_list = list(current_hashes) if current_hashes else ["__never__"]
        result = await self._session.execute(
            text("""
                DELETE FROM doc_chunks
                WHERE library_id = :library_id
                  AND content_hash != ALL(:hashes)
                RETURNING id
            """),
            {"library_id": library_id, "hashes": hashes_list},
        )
        deleted = len(result.fetchall())
        await self._session.commit()
        return deleted

    async def _get_existing_hashes(self, library_id: str) -> set[str]:
        result = await self._session.execute(
            select(DocChunk.content_hash).where(DocChunk.library_id == library_id)
        )
        return {row[0] for row in result.fetchall() if row[0]}
