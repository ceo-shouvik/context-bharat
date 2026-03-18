"""Library metadata repository."""
from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Library


class LibraryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, library_id: str) -> Library | None:
        result = await self._session.execute(
            select(Library).where(Library.library_id == library_id, Library.is_active == True)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> list[Library]:
        stmt = select(Library).where(Library.is_active == True)
        if category:
            stmt = stmt.where(Library.category == category)
        if query:
            stmt = stmt.where(
                or_(
                    Library.name.ilike(f"%{query}%"),
                    Library.description.ilike(f"%{query}%"),
                )
            )
        stmt = stmt.order_by(Library.chunk_count.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(self, library: Library) -> Library:
        existing = await self.get_by_id(library.library_id)
        if existing:
            for field in ["name", "description", "category", "tags", "chunk_count",
                          "last_indexed_at", "freshness_score"]:
                setattr(existing, field, getattr(library, field))
            await self._session.commit()
            return existing
        self._session.add(library)
        await self._session.commit()
        await self._session.refresh(library)
        return library

    async def count_active(self) -> int:
        result = await self._session.execute(
            select(func.count()).where(Library.is_active == True)
        )
        return result.scalar_one()
