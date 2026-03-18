"""Unit tests for document cleaner."""
from __future__ import annotations

from app.ingestion.crawlers.web_crawler import RawDocument
from app.ingestion.cleaner import clean_document


def _make_doc(content: str) -> RawDocument:
    return RawDocument(url="http://example.com", content=content, content_type="markdown")


def test_removes_cookie_banner():
    doc = _make_doc("# API Docs\n\nCookie policy link\n\n## Authentication\n\nUse Bearer tokens.")
    cleaned = clean_document(doc)
    assert "Cookie policy" not in cleaned.content
    assert "Authentication" in cleaned.content


def test_preserves_code_blocks():
    code = "```python\nimport razorpay\nclient = razorpay.Client()\n```"
    doc = _make_doc(f"# Guide\n\n{code}\n\nCookie policy")
    cleaned = clean_document(doc)
    assert "import razorpay" in cleaned.content
    assert "cookie policy" not in cleaned.content.lower()


def test_normalizes_excessive_blank_lines():
    doc = _make_doc("Line 1\n\n\n\n\n\nLine 2")
    cleaned = clean_document(doc)
    # Should have at most 3 consecutive newlines
    assert "\n\n\n\n" not in cleaned.content


def test_adds_space_after_hash_in_headers():
    doc = _make_doc("#NoSpace\n\n##AlsoNoSpace")
    cleaned = clean_document(doc)
    assert "# NoSpace" in cleaned.content
    assert "## AlsoNoSpace" in cleaned.content


def test_preserves_content_inside_code():
    """Cookie banners inside code blocks should NOT be removed."""
    doc = _make_doc("```\ncookie policy example here\n```")
    cleaned = clean_document(doc)
    assert "cookie policy example here" in cleaned.content
