"""
LLM-based chunk enrichment — adds metadata to each chunk using Claude Haiku.
Tags chunk type, detects API endpoints, programming languages, complexity.

This runs async in batches to minimise latency and cost.
Cost: ~$0.001 per 1000 chunks (Claude Haiku pricing).
"""
from __future__ import annotations

import json
import logging

from app.core.config import settings
from app.ingestion.chunker import Chunk

logger = logging.getLogger(__name__)
BATCH_SIZE = 20
ENRICH_PROMPT = """Analyze this documentation chunk. Return ONLY a JSON object, no other text:

{content}

JSON:
{{
  "chunk_type": "api_reference|guide|example|changelog|overview|error_reference",
  "has_code_example": true/false,
  "programming_languages": [],
  "api_endpoint": null
}}"""


async def enrich_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """Add LLM metadata to chunks. Non-destructive — enrichment failures return original chunks."""
    if not settings.ANTHROPIC_API_KEY:
        logger.debug("ANTHROPIC_API_KEY not set — skipping enrichment")
        return chunks

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    except ImportError:
        logger.warning("anthropic package not installed — skipping enrichment")
        return chunks

    enriched = []
    batches = [chunks[i:i + BATCH_SIZE] for i in range(0, len(chunks), BATCH_SIZE)]

    for batch in batches:
        tasks = [_enrich_single(client, chunk) for chunk in batch]
        import asyncio
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for chunk, result in zip(batch, results):
            if isinstance(result, Exception):
                enriched.append(chunk)
            else:
                enriched.append(result)

    return enriched


async def _enrich_single(client, chunk: Chunk) -> Chunk:
    """Enrich one chunk — returns original on any error."""
    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": ENRICH_PROMPT.format(content=chunk.content[:800]),
            }],
        )
        text = response.content[0].text.strip()
        metadata = json.loads(text)
        return Chunk(
            content=chunk.content,
            library_id=chunk.library_id,
            url=chunk.url,
            section=chunk.section,
            language=chunk.language,
            content_hash=chunk.content_hash,
            metadata={**chunk.metadata, **metadata},
            embedding=chunk.embedding,
        )
    except Exception:
        return chunk
