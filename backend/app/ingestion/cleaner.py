"""Document cleaner — normalize and clean raw crawled content."""
from __future__ import annotations

import re

from app.ingestion.crawlers.web_crawler import RawDocument

# Patterns that indicate navigation/boilerplate content
NAV_PATTERNS = [
    r"(skip to content|back to top|table of contents|on this page)",
    r"(previous|next)\s*[:|→|-]\s*\n",
    r"^(home|docs|api|guide|tutorial|reference)\s*[>/]\s*",
    r"© \d{4}.*?(all rights reserved|inc\.|ltd\.)",
    r"(subscribe to newsletter|follow us on|share on twitter|share on linkedin)",
    r"(cookie policy|privacy policy|terms of service)",
]

NAV_REGEX = re.compile("|".join(NAV_PATTERNS), re.IGNORECASE | re.MULTILINE)


def clean_document(doc: RawDocument) -> RawDocument:
    """
    Clean a raw document:
    - Remove navigation, footers, and cookie banners
    - Normalize whitespace (but preserve code block formatting)
    - Normalize markdown headers
    - Remove HTML comments

    Never modifies content inside ``` code blocks.
    """
    content = doc.content
    code_blocks: dict[str, str] = {}

    # Protect code blocks
    content = _protect_code_blocks(content, code_blocks)

    # Clean prose
    content = NAV_REGEX.sub("", content)
    content = re.sub(r"<!--[\s\S]*?-->", "", content)         # HTML comments
    content = re.sub(r"\n{4,}", "\n\n\n", content)            # Excessive blank lines
    content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)  # Trailing spaces
    content = re.sub(r"^[ \t]+", "", content, flags=re.MULTILINE)  # Leading spaces on lines

    # Normalize markdown headers (ensure space after #)
    content = re.sub(r"^(#{1,6})([^\s#])", r"\1 \2", content, flags=re.MULTILINE)

    # Restore code blocks
    content = _restore_code_blocks(content, code_blocks)

    return RawDocument(
        url=doc.url,
        content=content.strip(),
        content_type=doc.content_type,
        metadata=doc.metadata,
        library_id=doc.library_id,
    )


def _protect_code_blocks(text: str, code_blocks: dict) -> str:
    def replace(match):
        key = f"__CB_{len(code_blocks)}_CB__"
        code_blocks[key] = match.group(0)
        return key
    return re.sub(r"```[\s\S]*?```", replace, text)


def _restore_code_blocks(text: str, code_blocks: dict) -> str:
    for key, code in code_blocks.items():
        text = text.replace(key, code)
    return text
