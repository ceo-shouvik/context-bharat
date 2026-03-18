"""Shared test fixtures."""
from __future__ import annotations

import asyncio
import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Use in-memory SQLite for unit tests, Postgres for integration
TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/contextbharat_test",
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db():
    """Async DB session that rolls back after each test."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        from app.models.db import Base
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def sample_library_config():
    return {
        "library_id": "/razorpay/razorpay-sdk",
        "name": "Razorpay",
        "description": "India payment gateway",
        "category": "indian-fintech",
        "source": {"type": "web", "url": "https://razorpay.com/docs/", "crawl_depth": 1},
        "refresh_interval_hours": 24,
        "languages": ["en"],
        "tags": ["payments", "india"],
    }


@pytest.fixture
def sample_markdown_doc():
    return """# Razorpay Payment Links

## Create a Payment Link

Use the `/payment_links` endpoint to create a payment link.

```python
import razorpay
client = razorpay.Client(auth=("KEY_ID", "KEY_SECRET"))

response = client.payment_link.create({
    "amount": 50000,
    "currency": "INR",
    "description": "Payment for Order #1234",
    "customer": {"name": "Gaurav Kumar", "email": "gaurav@example.com"},
})
```

## Payment Link States

| State | Description |
|-------|-------------|
| created | Link created but not yet paid |
| paid | Payment completed |
| expired | Link has expired |

## Webhooks

Listen to `payment_link.paid` events for payment confirmations.
"""
