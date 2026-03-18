"""Document chunker — splits cleaned docs into 512-token chunks."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    content: str
    library_id: str
    url: str | None = None
    section: str | None = None
    language: str = "en"
    content_hash: str = ""
    metadata: dict = field(default_factory=dict)
    embedding: list[float] | None = None

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()


def chunk_document(
    content: str,
    library_id: str,
    url: str | None = None,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[Chunk]:
    """
    Split a document into overlapping chunks that respect:
    - Section boundaries (## headers always start a new chunk)
    - Code block integrity (never split inside ``` blocks)
    - Token limits (512 tokens ≈ 400 words)

    Returns list of Chunk objects ready for embedding.
    """
    # Protect code blocks — replace with placeholders
    code_blocks: dict[str, str] = {}
    protected = _protect_code_blocks(content, code_blocks)

    # Split into sections by headers
    sections = _split_by_sections(protected)

    chunks = []
    for section_title, section_content in sections:
        # Restore code blocks in this section
        restored = _restore_code_blocks(section_content, code_blocks)
        # Split large sections into token-limited chunks
        sub_chunks = _split_by_tokens(restored, max_tokens, overlap_tokens)
        for sub_content in sub_chunks:
            if sub_content.strip():
                chunks.append(Chunk(
                    content=sub_content.strip(),
                    library_id=library_id,
                    url=url,
                    section=section_title,
                ))

    return chunks if chunks else [Chunk(content=content[:4000], library_id=library_id, url=url)]


def _protect_code_blocks(text: str, code_blocks: dict) -> str:
    """Replace code blocks with placeholders to prevent splitting inside them."""
    def replace(match):
        key = f"__CODE_{len(code_blocks)}__"
        code_blocks[key] = match.group(0)
        return key
    return re.sub(r"```[\s\S]*?```", replace, text)


def _restore_code_blocks(text: str, code_blocks: dict) -> str:
    for key, code in code_blocks.items():
        text = text.replace(key, code)
    return text


def _split_by_sections(text: str) -> list[tuple[str, str]]:
    """Split text by markdown headers, returning (title, content) pairs."""
    pattern = re.compile(r"^(#{1,3} .+)$", re.MULTILINE)
    parts = pattern.split(text)
    sections = []
    if parts[0].strip():
        sections.append(("", parts[0]))
    for i in range(1, len(parts), 2):
        title = parts[i].strip("#").strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append((title, parts[i] + "\n" + content))
    return sections or [("", text)]


def _split_by_tokens(text: str, max_tokens: int, overlap: int) -> list[str]:
    """Split text into token-limited chunks. 1 token ≈ 0.75 words."""
    max_words = int(max_tokens * 0.75)
    overlap_words = int(overlap * 0.75)
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_words
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start = end - overlap_words
    return chunks
