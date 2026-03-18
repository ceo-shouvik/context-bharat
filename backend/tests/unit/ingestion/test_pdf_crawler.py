"""Unit tests for PDFCrawler."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


def test_table_to_markdown_basic():
    from app.ingestion.crawlers.pdf_crawler import PDFCrawler

    table = [
        ["Header 1", "Header 2", "Header 3"],
        ["Row 1A", "Row 1B", "Row 1C"],
        ["Row 2A", "Row 2B", "Row 2C"],
    ]
    result = PDFCrawler._table_to_markdown(table)

    assert "| Header 1 | Header 2 | Header 3 |" in result
    assert "| --- | --- | --- |" in result
    assert "| Row 1A | Row 1B | Row 1C |" in result


def test_table_to_markdown_handles_none_cells():
    from app.ingestion.crawlers.pdf_crawler import PDFCrawler

    table = [["A", None, "C"], ["D", "E", None]]
    result = PDFCrawler._table_to_markdown(table)
    assert "A" in result
    assert "C" in result


def test_table_to_markdown_empty():
    from app.ingestion.crawlers.pdf_crawler import PDFCrawler
    assert PDFCrawler._table_to_markdown([]) == ""
    assert PDFCrawler._table_to_markdown([[]]) == ""
