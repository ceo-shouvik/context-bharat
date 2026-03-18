"""Unit tests for LibraryService."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.db import Library


def _make_library(**kwargs) -> Library:
    defaults = dict(
        id="00000000-0000-0000-0000-000000000001",
        library_id="/razorpay/razorpay-sdk",
        name="Razorpay",
        description="India payment gateway",
        category="indian-fintech",
        tags=["payments", "india"],
        chunk_count=100,
        freshness_score=0.95,
        is_active=True,
        last_indexed_at=None,
    )
    defaults.update(kwargs)
    lib = MagicMock(spec=Library)
    for k, v in defaults.items():
        setattr(lib, k, v)
    return lib


@pytest.mark.asyncio
async def test_list_returns_library_results():
    from app.services.library_service import LibraryService

    mock_libs = [
        _make_library(library_id="/razorpay/razorpay-sdk", name="Razorpay"),
        _make_library(library_id="/zerodha/kite-api", name="Zerodha Kite API"),
    ]

    with patch("app.services.library_service.AsyncSessionLocal") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session_cls.return_value = mock_session

        with patch("app.services.library_service.LibraryRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.search = AsyncMock(return_value=mock_libs)
            mock_repo_cls.return_value = mock_repo

            service = LibraryService()
            results = await service.list()

    assert len(results) == 2
    assert results[0].library_id == "/razorpay/razorpay-sdk"
    assert results[1].name == "Zerodha Kite API"


@pytest.mark.asyncio
async def test_resolve_exact_name_match():
    from app.services.library_service import LibraryService

    mock_libs = [
        _make_library(library_id="/razorpay/razorpay-sdk", name="Razorpay"),
        _make_library(library_id="/zerodha/kite-api", name="Zerodha Kite API"),
    ]

    with patch("app.services.library_service.AsyncSessionLocal") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session_cls.return_value = mock_session

        with patch("app.services.library_service.LibraryRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.search = AsyncMock(return_value=mock_libs)
            mock_repo_cls.return_value = mock_repo

            service = LibraryService()
            result = await service.resolve(
                query="how to create razorpay payment link",
                library_name="Razorpay",
            )

    assert result.library_id == "/razorpay/razorpay-sdk"
    assert result.confidence >= 0.9


@pytest.mark.asyncio
async def test_resolve_partial_name_match():
    from app.services.library_service import LibraryService

    mock_libs = [_make_library(library_id="/zerodha/kite-api", name="Zerodha Kite API")]

    with patch("app.services.library_service.AsyncSessionLocal") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session_cls.return_value = mock_session

        with patch("app.services.library_service.LibraryRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.search = AsyncMock(return_value=mock_libs)
            mock_repo_cls.return_value = mock_repo

            service = LibraryService()
            result = await service.resolve(
                query="place market order zerodha kite",
                library_name="kite",
            )

    assert "zerodha" in result.library_id


@pytest.mark.asyncio
async def test_resolve_not_found_raises_404():
    from fastapi import HTTPException
    from app.services.library_service import LibraryService

    with patch("app.services.library_service.AsyncSessionLocal") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session_cls.return_value = mock_session

        with patch("app.services.library_service.LibraryRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.search = AsyncMock(return_value=[])
            mock_repo_cls.return_value = mock_repo

            service = LibraryService()
            with pytest.raises(HTTPException) as exc_info:
                await service.resolve(
                    query="totally nonexistent library xyz",
                    library_name="xyz-nonexistent-123",
                )

    assert exc_info.value.status_code == 404
