"""Integration tests — documentation query endpoint."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.models.schemas import QueryDocsResponse


@pytest.mark.asyncio
async def test_query_docs_success():
    """POST /v1/docs/query returns documentation for a known library."""
    mock_response = QueryDocsResponse(
        docs="## Create a Payment Link\n\nUse `POST /payment_links`...",
        library_id="/razorpay/razorpay-sdk",
        library_name="Razorpay",
        sources=["https://razorpay.com/docs/payment-links/"],
        freshness_score=0.95,
        language="en",
        token_count=120,
    )

    with patch("app.services.search_service.SearchService.query", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = mock_response

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/docs/query",
                json={
                    "library_id": "/razorpay/razorpay-sdk",
                    "query": "create payment link",
                    "token_budget": 5000,
                    "language": "en",
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert "payment" in data["docs"].lower()
    assert data["library_id"] == "/razorpay/razorpay-sdk"
    assert data["library_name"] == "Razorpay"
    assert len(data["sources"]) > 0


@pytest.mark.asyncio
async def test_query_docs_library_not_found():
    """POST /v1/docs/query returns 404 for unknown library."""
    with patch("app.services.search_service.SearchService.query", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/docs/query",
                json={
                    "library_id": "/nonexistent/library",
                    "query": "anything",
                },
            )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_query_docs_with_language():
    """POST /v1/docs/query respects language parameter."""
    mock_response = QueryDocsResponse(
        docs="## भुगतान लिंक बनाएं\n\nRazorpay API...",
        library_id="/razorpay/razorpay-sdk",
        library_name="Razorpay",
        sources=["https://razorpay.com/docs/payment-links/"],
        freshness_score=0.95,
        language="hi",
        token_count=100,
    )

    with patch("app.services.search_service.SearchService.query", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = mock_response

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/docs/query",
                json={
                    "library_id": "/razorpay/razorpay-sdk",
                    "query": "payment link",
                    "language": "hi",
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "hi"


@pytest.mark.asyncio
async def test_query_docs_with_token_budget():
    """POST /v1/docs/query respects custom token budget."""
    mock_response = QueryDocsResponse(
        docs="Short response.",
        library_id="/razorpay/razorpay-sdk",
        library_name="Razorpay",
        sources=[],
        freshness_score=0.95,
        language="en",
        token_count=5,
    )

    with patch("app.services.search_service.SearchService.query", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = mock_response

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/docs/query",
                json={
                    "library_id": "/razorpay/razorpay-sdk",
                    "query": "payment link",
                    "token_budget": 500,
                },
            )

    assert response.status_code == 200
    mock_query.assert_called_once()
    call_kwargs = mock_query.call_args
    assert call_kwargs[1]["token_budget"] == 500 or call_kwargs[0][2] == 500


@pytest.mark.asyncio
async def test_query_docs_invalid_language():
    """POST /v1/docs/query rejects invalid language code."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/v1/docs/query",
            json={
                "library_id": "/razorpay/razorpay-sdk",
                "query": "payment link",
                "language": "xx",
            },
        )

    assert response.status_code == 422  # Pydantic validation error
