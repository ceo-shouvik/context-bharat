"""Local embedding generation using fastembed — zero API cost."""
from __future__ import annotations

import logging
from typing import ClassVar

from app.ingestion.chunker import Chunk

logger = logging.getLogger(__name__)

BATCH_SIZE = 256
MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMS = 384

# Singleton model instance — loaded once, reused across calls
_model = None


def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _model = TextEmbedding(model_name=MODEL_NAME)
        logger.info("Embedding model loaded")
    return _model


async def embed_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """
    Generate embeddings for all chunks using local fastembed model.
    BAAI/bge-small-en-v1.5: 384 dimensions, runs locally, zero cost.
    """
    if not chunks:
        return chunks

    model = _get_model()
    texts = [c.content for c in chunks]

    logger.info(f"Embedding {len(chunks)} chunks locally with {MODEL_NAME}")
    embeddings = list(model.embed(texts, batch_size=BATCH_SIZE))
    logger.info(f"Embedded {len(chunks)} chunks (local, $0.00)")

    return [
        Chunk(
            content=chunk.content,
            library_id=chunk.library_id,
            url=chunk.url,
            section=chunk.section,
            language=chunk.language,
            content_hash=chunk.content_hash,
            metadata={**chunk.metadata, "embedding_model": MODEL_NAME},
            embedding=embedding.tolist(),
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]


async def embed_single(text: str) -> list[float]:
    """Embed a single text — used for query-time embedding."""
    model = _get_model()
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()
