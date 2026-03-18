"""PDF crawler — handles text-based PDFs (pdfplumber) and scanned PDFs (Tesseract OCR)."""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import httpx

from app.ingestion.crawlers.web_crawler import RawDocument

logger = logging.getLogger(__name__)

WORDS_PER_PAGE_THRESHOLD = 80  # Below this → assume scanned PDF, use OCR


class PDFCrawler:
    """
    Handles government PDFs, API specs distributed as PDFs, and scanned documents.

    Strategy:
    1. Try pdfplumber (text-based PDF) → table extraction + structured text
    2. If avg words/page < threshold → fall back to Tesseract OCR
    3. Store OCR confidence score in metadata for quality flagging
    """

    async def crawl(self, pdf_urls: list[str], config: dict) -> list[RawDocument]:
        docs = []
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            for url in pdf_urls:
                try:
                    doc = await self._crawl_single(client, url, config)
                    if doc:
                        docs.append(doc)
                except Exception as e:
                    logger.error(f"PDF crawl failed for {url}: {e}")
        return docs

    async def _crawl_single(
        self, client: httpx.AsyncClient, url: str, config: dict
    ) -> RawDocument | None:
        logger.info(f"Downloading PDF: {url}")
        response = await client.get(url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(response.content)
            pdf_path = Path(tmp.name)

        try:
            content, metadata = self._extract_text(pdf_path)
            if not content.strip():
                logger.warning(f"Empty content extracted from {url}")
                return None

            return RawDocument(
                url=url,
                content=content,
                content_type="markdown",
                metadata={**metadata, "source_type": "pdf"},
                library_id=config.get("library_id", ""),
            )
        finally:
            pdf_path.unlink(missing_ok=True)

    def _extract_text(self, pdf_path: Path) -> tuple[str, dict]:
        """Extract text from PDF, falling back to OCR for scanned docs."""
        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber not installed — run: pip install pdfplumber")
            raise

        pages_text = []
        total_words = 0

        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""
                # Extract tables → Markdown
                for table in page.extract_tables():
                    if table:
                        page_text += "\n" + self._table_to_markdown(table) + "\n"
                pages_text.append(page_text)
                total_words += len(page_text.split())

        avg_words_per_page = total_words / max(num_pages, 1)

        if avg_words_per_page < WORDS_PER_PAGE_THRESHOLD:
            logger.info(
                f"Low text density ({avg_words_per_page:.1f} words/page) — using OCR"
            )
            text, confidence = self._ocr_pdf(pdf_path)
            return text, {"extraction_method": "ocr", "ocr_confidence": confidence}

        combined = "\n\n".join(p for p in pages_text if p.strip())
        return combined, {"extraction_method": "pdfplumber", "page_count": num_pages}

    def _ocr_pdf(self, pdf_path: Path) -> tuple[str, float]:
        """OCR a scanned PDF using Tesseract via pdf2image."""
        try:
            import pytesseract
            from pdf2image import convert_from_path
        except ImportError:
            logger.error("pytesseract/pdf2image not installed")
            raise

        images = convert_from_path(pdf_path, dpi=300)
        pages = []
        confidences = []

        for image in images:
            data = pytesseract.image_to_data(
                image, lang="eng", output_type=pytesseract.Output.DICT
            )
            # Confidence scores (filter out -1 which means no text)
            conf_values = [c for c in data["conf"] if c != -1]
            if conf_values:
                confidences.append(sum(conf_values) / len(conf_values))
            pages.append(pytesseract.image_to_string(image, lang="eng"))

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return "\n\n".join(pages), avg_confidence / 100.0  # Normalize to 0-1

    @staticmethod
    def _table_to_markdown(table: list[list]) -> str:
        """Convert pdfplumber table to Markdown format."""
        if not table or not table[0]:
            return ""
        rows = []
        for i, row in enumerate(table):
            cells = [str(cell or "").strip() for cell in row]
            rows.append("| " + " | ".join(cells) + " |")
            if i == 0:
                rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
        return "\n".join(rows)
