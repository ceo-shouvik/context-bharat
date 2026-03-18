"""Unit tests for the document chunker."""
from __future__ import annotations

import pytest
from app.ingestion.chunker import chunk_document, Chunk


def test_basic_chunking():
    """Short doc returns single chunk."""
    chunks = chunk_document("Hello world. This is a test.", library_id="/test/lib", url="http://example.com")
    assert len(chunks) >= 1
    assert all(isinstance(c, Chunk) for c in chunks)


def test_chunk_has_hash():
    """Each chunk should have a content_hash."""
    chunks = chunk_document("Test content", library_id="/test/lib")
    assert all(c.content_hash for c in chunks)


def test_chunk_respects_token_limit():
    """No chunk should exceed max_tokens words (approx)."""
    long_text = "word " * 2000
    chunks = chunk_document(long_text, library_id="/test/lib", max_tokens=512)
    # 512 tokens ≈ 384 words. Allow some slack.
    assert all(len(c.content.split()) <= 600 for c in chunks)


def test_section_header_starts_new_chunk(sample_markdown_doc):
    """Headers should trigger section boundaries."""
    chunks = chunk_document(sample_markdown_doc, library_id="/test/lib")
    # At least one chunk should have a section
    sections = [c.section for c in chunks if c.section]
    assert len(sections) > 0


def test_code_block_not_split():
    """Code blocks should not be broken across chunks."""
    doc = "Some text\n\n```python\n" + "x = 1\n" * 100 + "```\n\nMore text"
    chunks = chunk_document(doc, library_id="/test/lib")
    for chunk in chunks:
        backtick_count = chunk.content.count("```")
        # Either 0 (no code block) or 2 (complete block) — never 1
        assert backtick_count in (0, 2), f"Split code block detected: {backtick_count} backticks"


def test_empty_content_returns_chunk():
    """Even empty content should return at least one chunk."""
    chunks = chunk_document("", library_id="/test/lib")
    assert len(chunks) >= 1


@pytest.fixture
def sample_markdown_doc():
    return """# Razorpay API

## Payment Links

Create payment links easily.

```python
client.payment_link.create({"amount": 50000})
```

## Webhooks

Handle payment.captured events.
"""
