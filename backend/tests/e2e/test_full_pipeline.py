"""
E2E test — full ingestion + query cycle.
Requires: local Postgres + pgvector + OpenAI API key.
Skip in CI unless E2E_TESTS=true.
"""
from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(
    os.getenv("E2E_TESTS") != "true",
    reason="E2E tests require real infrastructure. Set E2E_TESTS=true to run.",
)
@pytest.mark.asyncio
async def test_full_ingestion_and_query():
    """
    Full cycle: ingest Razorpay docs → query → verify results.
    This test validates the entire pipeline end-to-end.
    """
    from app.ingestion.pipeline import run_ingestion
    from app.services.search_service import SearchService
    from app.models.schemas import Language

    # Step 1: Run ingestion
    result = await run_ingestion("razorpay", force_refresh=True)
    assert result.status == "success"
    assert result.chunks_indexed > 0
    print(f"Indexed {result.chunks_indexed} chunks, ${result.embedding_cost_usd:.4f} cost")

    # Step 2: Query
    service = SearchService()
    response = await service.query(
        library_id="/razorpay/razorpay-sdk",
        query="how to create a payment link",
        token_budget=2000,
        language=Language.EN,
    )

    assert response is not None
    assert response.library_id == "/razorpay/razorpay-sdk"
    assert len(response.docs) > 100
    assert response.token_count > 0
    print(f"Query returned {response.token_count} tokens")

    # Step 3: Verify relevance — result should mention payment links
    docs_lower = response.docs.lower()
    assert any(term in docs_lower for term in ["payment", "link", "razorpay"])
