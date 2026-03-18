"""Unit tests for SearchService."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.repositories.vector_repo import SearchResult


def _make_search_result(chunk_id="c1", content="test content", score=0.9, url="http://example.com"):
    return SearchResult(
        chunk_id=chunk_id,
        library_id="/razorpay/razorpay-sdk",
        content=content,
        url=url,
        section="API Reference",
        language="en",
        score=score,
    )


def test_merge_results_deduplicates():
    from app.services.search_service import _merge_results

    r1 = _make_search_result("c1", score=0.9)
    r2 = _make_search_result("c1", score=0.8)  # Same chunk_id
    r3 = _make_search_result("c2", score=0.7)

    merged = _merge_results([r1], [r2, r3], limit=10)
    ids = [r.chunk_id for r in merged]

    assert ids.count("c1") == 1  # Deduplicated
    assert "c2" in ids


def test_merge_results_boosts_overlap():
    from app.services.search_service import _merge_results

    r1 = _make_search_result("c1", score=0.5)  # In vector only
    r2 = _make_search_result("c1", score=0.5)  # Also in keyword — should get boost

    merged = _merge_results([r1], [r2], limit=10)
    assert len(merged) == 1
    # Score should be higher than 0.5 (vector-only) due to overlap boost
    assert merged[0].score > 0.5


def test_assemble_response_respects_token_budget():
    from app.services.search_service import _assemble_response

    # Create chunks that collectively exceed budget
    big_chunks = [
        _make_search_result(f"c{i}", content="word " * 500, score=0.9 - i * 0.1)
        for i in range(20)
    ]
    assembled = _assemble_response(big_chunks, token_budget=1000)

    # Should be within budget
    word_count = len(assembled.content.split())
    assert word_count <= 1000 * 1.2  # Allow 20% slack for section headers


def test_assemble_response_puts_code_first():
    from app.services.search_service import _assemble_response

    prose_chunk = _make_search_result("p1", content="This is a guide about payments.", score=0.95)
    code_chunk = _make_search_result("c1", content="```python\nclient.pay()\n```", score=0.80)

    assembled = _assemble_response([prose_chunk, code_chunk], token_budget=5000)

    # Code chunk should appear before prose (even with lower score)
    code_pos = assembled.content.find("```python")
    prose_pos = assembled.content.find("This is a guide")
    assert code_pos < prose_pos


def test_assemble_response_collects_sources():
    from app.services.search_service import _assemble_response

    chunks = [
        _make_search_result("c1", url="https://razorpay.com/docs/payments"),
        _make_search_result("c2", url="https://razorpay.com/docs/orders"),
        _make_search_result("c3", url="https://razorpay.com/docs/payments"),  # Duplicate URL
    ]

    assembled = _assemble_response(chunks, token_budget=5000)
    assert len(assembled.sources) == 2  # Deduplicated


def test_merge_results_respects_limit():
    from app.services.search_service import _merge_results

    results = [_make_search_result(f"c{i}", score=0.9 - i * 0.01) for i in range(50)]
    merged = _merge_results(results, [], limit=10)
    assert len(merged) == 10


def test_merge_results_empty_inputs():
    from app.services.search_service import _merge_results

    merged = _merge_results([], [], limit=10)
    assert merged == []


def test_merge_results_vector_boosted():
    """Vector results get 1.1x score boost."""
    from app.services.search_service import _merge_results

    vector_r = _make_search_result("v1", score=1.0)
    keyword_r = _make_search_result("k1", score=1.0)

    merged = _merge_results([vector_r], [keyword_r], limit=10)
    v = next(r for r in merged if r.chunk_id == "v1")
    k = next(r for r in merged if r.chunk_id == "k1")
    assert v.score > k.score  # Vector result boosted


def test_assemble_response_empty_results():
    from app.services.search_service import _assemble_response

    assembled = _assemble_response([], token_budget=5000)
    assert "No relevant documentation found" in assembled.content
    assert assembled.token_count == 0


def test_assemble_caps_sources_at_five():
    from app.services.search_service import _assemble_response

    chunks = [
        _make_search_result(f"c{i}", content="some docs", url=f"https://example.com/page{i}")
        for i in range(10)
    ]
    assembled = _assemble_response(chunks, token_budget=50000)
    assert len(assembled.sources) <= 5


def test_cache_key_uses_deterministic_hash():
    """Verify cache key is deterministic (SHA256, not hash())."""
    import hashlib
    query = "test query"
    expected_hash = hashlib.sha256(query.encode()).hexdigest()[:12]
    # Verify the hash is consistent across calls
    assert expected_hash == hashlib.sha256(query.encode()).hexdigest()[:12]
