"""OpenAI embedding generation — batched for cost efficiency."""
from __future__ import annotations

import logging

from app.core.config import settings
from app.ingestion.chunker import Chunk

logger = logging.getLogger(__name__)

BATCH_SIZE = 100  # OpenAI embedding batch limit


async def embed_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """
    Generate embeddings for all chunks using OpenAI text-embedding-3-small.
    Processes in batches of 100 (50% cost reduction vs individual calls).
    Returns chunks with embedding field populated.
    """
    try:
        from openai import AsyncOpenAI
    except ImportError:
        logger.error("openai package not installed")
        raise

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    batches = [chunks[i:i + BATCH_SIZE] for i in range(0, len(chunks), BATCH_SIZE)]
    all_embeddings: list[list[float]] = []

    total_tokens = 0
    for i, batch in enumerate(batches):
        logger.info(f"Embedding batch {i + 1}/{len(batches)} ({len(batch)} chunks)")
        texts = [c.content for c in batch]
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts,
            encoding_format="float",
        )
        all_embeddings.extend([e.embedding for e in response.data])
        total_tokens += response.usage.total_tokens

    cost_usd = (total_tokens / 1_000_000) * 0.02  # text-embedding-3-small pricing
    logger.info(f"Embedded {len(chunks)} chunks | {total_tokens} tokens | ~${cost_usd:.4f}")

    return [
        Chunk(
            content=chunk.content,
            library_id=chunk.library_id,
            url=chunk.url,
            section=chunk.section,
            language=chunk.language,
            content_hash=chunk.content_hash,
            metadata={**chunk.metadata, "embedding_model": settings.EMBEDDING_MODEL},
            embedding=embedding,
        )
        for chunk, embedding in zip(chunks, all_embeddings)
    ]


async def embed_single(text: str) -> list[float]:
    """Embed a single text — used for query-time embedding."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=[text],
        encoding_format="float",
    )
    return response.data[0].embedding
