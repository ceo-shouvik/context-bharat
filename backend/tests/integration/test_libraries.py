"""Integration tests — library resolution and listing endpoints."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.models.db import Library


def _mock_library(**kwargs) -> MagicMock:
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
        npm_package="razorpay",
        pypi_package="razorpay",
        github_repo="razorpay/razorpay-node",
    )
    defaults.update(kwargs)
    lib = MagicMock(spec=Library)
    for k, v in defaults.items():
        setattr(lib, k, v)
    return lib


@pytest.mark.asyncio
async def test_list_libraries_returns_200():
    """GET /v1/libraries returns list of libraries."""
    mock_libs = [
        _mock_library(library_id="/razorpay/razorpay-sdk", name="Razorpay"),
        _mock_library(library_id="/cashfree/cashfree-pg", name="Cashfree PG", category="indian-fintech"),
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

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/v1/libraries")

    assert response.status_code == 200
    data = response.json()
    assert "libraries" in data
    assert data["total"] == 2
    assert data["libraries"][0]["library_id"] == "/razorpay/razorpay-sdk"


@pytest.mark.asyncio
async def test_list_libraries_with_category_filter():
    """GET /v1/libraries?category=indian-fintech filters correctly."""
    mock_libs = [_mock_library()]

    with patch("app.services.library_service.AsyncSessionLocal") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session_cls.return_value = mock_session

        with patch("app.services.library_service.LibraryRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.search = AsyncMock(return_value=mock_libs)
            mock_repo_cls.return_value = mock_repo

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/v1/libraries?category=indian-fintech")

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "indian-fintech"


@pytest.mark.asyncio
async def test_resolve_library_exact_match():
    """POST /v1/libraries/resolve returns exact match with high confidence."""
    mock_libs = [_mock_library()]

    with patch("app.services.library_service.AsyncSessionLocal") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session_cls.return_value = mock_session

        with patch("app.services.library_service.LibraryRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.search = AsyncMock(return_value=mock_libs)
            mock_repo_cls.return_value = mock_repo

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/v1/libraries/resolve",
                    json={"query": "razorpay payment link", "library_name": "Razorpay"},
                )

    assert response.status_code == 200
    data = response.json()
    assert data["library_id"] == "/razorpay/razorpay-sdk"
    assert data["confidence"] >= 0.9


@pytest.mark.asyncio
async def test_resolve_library_fuzzy_match():
    """POST /v1/libraries/resolve finds partial name match."""
    mock_libs = [
        _mock_library(library_id="/zerodha/kite-api", name="Zerodha Kite API"),
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

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/v1/libraries/resolve",
                    json={"query": "kite trading api", "library_name": "kite"},
                )

    assert response.status_code == 200
    data = response.json()
    assert "zerodha" in data["library_id"]


@pytest.mark.asyncio
async def test_resolve_library_not_found():
    """POST /v1/libraries/resolve returns 404 for unknown library."""
    with patch("app.services.library_service.AsyncSessionLocal") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session_cls.return_value = mock_session

        with patch("app.services.library_service.LibraryRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.search = AsyncMock(return_value=[])
            mock_repo_cls.return_value = mock_repo

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/v1/libraries/resolve",
                    json={"query": "nonexistent", "library_name": "xyz-nonexistent-lib-123"},
                )

    assert response.status_code == 404
