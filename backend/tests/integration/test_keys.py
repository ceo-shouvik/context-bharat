"""Integration tests — API key management endpoints."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app


@pytest.mark.asyncio
async def test_create_api_key_unauthorized():
    """POST /v1/keys without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/v1/keys", json={"name": "test-key"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_api_keys_unauthorized():
    """GET /v1/keys without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/v1/keys")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_revoke_api_key_unauthorized():
    """DELETE /v1/keys/{id} without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/v1/keys/00000000-0000-0000-0000-000000000001")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_api_key_with_valid_token():
    """POST /v1/keys with valid JWT creates a key."""
    from app.dependencies import get_current_user
    from app.core.database import get_db

    mock_user_id = "00000000-0000-0000-0000-000000000099"
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: mock_user_id

    async def _override_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/keys",
                json={"name": "my-test-key"},
                headers={"Authorization": "Bearer fake-jwt-token"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["key"].startswith("c7i_")
        assert data["tier"] == "free"
        assert data["daily_limit"] == 100
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_api_keys_with_valid_token():
    """GET /v1/keys with valid JWT returns user's keys."""
    from app.models.db import ApiKey
    from app.dependencies import get_current_user
    from app.core.database import get_db
    from datetime import datetime, timezone

    mock_user_id = "00000000-0000-0000-0000-000000000099"

    mock_key = MagicMock(spec=ApiKey)
    mock_key.id = "00000000-0000-0000-0000-000000000001"
    mock_key.key_prefix = "c7i_test1234"
    mock_key.name = "my-key"
    mock_key.tier = "free"
    mock_key.daily_limit = 100
    mock_key.is_active = True
    mock_key.last_used_at = None
    mock_key.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_key]
    mock_session.execute = AsyncMock(return_value=mock_result)

    app.dependency_overrides[get_current_user] = lambda: mock_user_id

    async def _override_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/v1/keys",
                headers={"Authorization": "Bearer fake-jwt-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["key_prefix"] == "c7i_test1234"
    finally:
        app.dependency_overrides.clear()
