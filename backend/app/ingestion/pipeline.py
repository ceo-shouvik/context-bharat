"""
Context Bharat — Ingestion Pipeline Orchestrator

Stages:
  1. Load config from backend/config/libraries/{library_id}.json
  2. Freshness check — skip if recently indexed (unless force=True)
  3. Crawl — source-type dispatch (web / pdf / github / multi)
  4. Clean — remove nav, normalize whitespace, protect code blocks
  5. Chunk — 512-token windows, section-boundary-aware
  6. Enrich — LLM metadata tagging (Claude Haiku, async, batched)
  7. Embed — OpenAI text-embedding-3-small, batched
  8. Translate — Sarvam AI for non-English language configs
  9. Upsert — pgvector bulk insert/update, stale chunk deletion
  10. Update library metadata — freshness score, chunk count, timestamp

See knowledge-base/ingestion-pipeline.md for full specification.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent.parent / "config" / "libraries"


@dataclass
class IngestionResult:
    library_id: str
    chunks_indexed: int = 0
    chunks_deleted: int = 0
    errors: list[dict] = field(default_factory=list)
    duration_seconds: int = 0
    embedding_cost_usd: float = 0.0
    status: str = "success"


async def run_ingestion(
    library_id: str,
    force_refresh: bool = False,
) -> IngestionResult:
    """
    Run the complete ingestion pipeline for one library.

    Args:
        library_id: slug like 'razorpay' or canonical '/razorpay/razorpay-sdk'
        force_refresh: skip freshness check and re-index regardless
    """
    start_time = time.time()
    result = IngestionResult(library_id=library_id)

    # ── Stage 1: Load config ─────────────────────────────────────────────────
    config = _load_config(library_id)
    canonical_id = config["library_id"]
    logger.info(f"[{canonical_id}] Starting ingestion force={force_refresh}")

    # ── Stage 2: Freshness check ─────────────────────────────────────────────
    from app.core.database import AsyncSessionLocal
    from app.repositories.library_repo import LibraryRepository
    from app.models.db import Library, IngestionRun

    async with AsyncSessionLocal() as session:
        repo = LibraryRepository(session)
        library = await repo.get_by_id(canonical_id)

        if not force_refresh and library and library.last_indexed_at:
            hours_since = (datetime.now(timezone.utc) - library.last_indexed_at).total_seconds() / 3600
            refresh_interval = config.get("refresh_interval_hours", 24)
            if hours_since < refresh_interval:
                logger.info(f"[{canonical_id}] Fresh ({hours_since:.1f}h old, interval={refresh_interval}h) — skipping")
                return IngestionResult(library_id=canonical_id, status="skipped")

        # Ensure library row exists
        if not library:
            library = Library(
                id=uuid.uuid4(),
                library_id=canonical_id,
                name=config["name"],
                description=config.get("description"),
                category=config["category"],
                tags=config.get("tags", []),
                npm_package=config.get("npm_package"),
                pypi_package=config.get("pypi_package"),
                github_repo=config.get("github_repo"),
            )
            session.add(library)
            await session.commit()

        # Create ingestion run record
        run = IngestionRun(
            id=uuid.uuid4(),
            library_id=canonical_id,
            status="running",
            triggered_by="manual",
            started_at=datetime.now(timezone.utc),
        )
        session.add(run)
        await session.commit()
        run_id = run.id

    # ── Stage 3: Crawl ───────────────────────────────────────────────────────
    raw_docs = await _crawl(config)
    logger.info(f"[{canonical_id}] Crawled {len(raw_docs)} documents")

    if not raw_docs:
        result.errors.append({"stage": "crawl", "error": "No documents returned"})
        result.status = "failed"
        await _finalize_run(run_id, result)
        return result

    # ── Stage 4: Clean ───────────────────────────────────────────────────────
    from app.ingestion.cleaner import clean_document
    cleaned = [clean_document(doc) for doc in raw_docs]
    logger.info(f"[{canonical_id}] Cleaned {len(cleaned)} documents")

    # ── Stage 5: Chunk ───────────────────────────────────────────────────────
    from app.ingestion.chunker import chunk_document
    all_chunks = []
    for doc in cleaned:
        chunks = chunk_document(
            content=doc.content,
            library_id=canonical_id,
            url=doc.url,
            max_tokens=settings.DEFAULT_CHUNK_SIZE,
            overlap_tokens=settings.DEFAULT_CHUNK_OVERLAP,
        )
        all_chunks.extend(chunks)
    logger.info(f"[{canonical_id}] Created {len(all_chunks)} chunks")

    # ── Stage 6: Enrich ──────────────────────────────────────────────────────
    try:
        from app.ingestion.enricher import enrich_chunks
        all_chunks = await enrich_chunks(all_chunks)
    except Exception as e:
        logger.warning(f"[{canonical_id}] Enrichment failed (non-fatal): {e}")

    # ── Stage 7: Embed ───────────────────────────────────────────────────────
    from app.ingestion.embedder import embed_chunks
    embedded_chunks = await embed_chunks(all_chunks)

    # Estimate embedding cost
    total_words = sum(len(c.content.split()) for c in embedded_chunks)
    total_tokens = int(total_words / 0.75)
    result.embedding_cost_usd = (total_tokens / 1_000_000) * 0.02

    # ── Stage 8: Translate ───────────────────────────────────────────────────
    languages = config.get("languages", ["en"])
    translated_chunks = []
    if len(languages) > 1:
        from app.services.translation_service import TranslationService
        translator = TranslationService()
        for lang in languages:
            if lang == "en":
                continue
            try:
                lang_chunks = await translator.translate_chunks(embedded_chunks, target_lang=lang)
                translated_chunks.extend(lang_chunks)
                logger.info(f"[{canonical_id}] Translated {len(lang_chunks)} chunks to {lang}")
            except Exception as e:
                logger.warning(f"[{canonical_id}] Translation to {lang} failed: {e}")
                result.errors.append({"stage": "translate", "lang": lang, "error": str(e)})

    final_chunks = embedded_chunks + translated_chunks

    # ── Stage 9: Upsert ──────────────────────────────────────────────────────
    from app.models.db import DocChunk
    from app.repositories.vector_repo import VectorRepository

    async with AsyncSessionLocal() as session:
        vector_repo = VectorRepository(session)

        db_chunks = [
            DocChunk(
                id=uuid.uuid4(),
                library_id=chunk.library_id,
                content=chunk.content,
                embedding=chunk.embedding,
                url=chunk.url,
                section=chunk.section,
                language=chunk.language,
                content_hash=chunk.content_hash,
                chunk_metadata=chunk.metadata,
            )
            for chunk in final_chunks
            if chunk.embedding is not None
        ]

        inserted = await vector_repo.bulk_upsert(db_chunks)
        current_hashes = {c.content_hash for c in final_chunks if c.content_hash}
        deleted = await vector_repo.delete_stale(canonical_id, current_hashes)

        result.chunks_indexed = inserted
        result.chunks_deleted = deleted

    # ── Stage 10: Update library metadata ────────────────────────────────────
    async with AsyncSessionLocal() as session:
        repo = LibraryRepository(session)
        lib = await repo.get_by_id(canonical_id)
        if lib:
            lib.last_indexed_at = datetime.now(timezone.utc)
            lib.chunk_count = len(final_chunks)
            lib.freshness_score = 1.0
            await session.commit()

    result.duration_seconds = int(time.time() - start_time)
    result.status = "success"

    logger.info(
        f"[{canonical_id}] Ingestion complete: "
        f"{result.chunks_indexed} indexed, {result.chunks_deleted} deleted, "
        f"{result.duration_seconds}s, ${result.embedding_cost_usd:.4f}"
    )

    await _finalize_run(run_id, result)
    return result


def _load_config(library_id: str) -> dict:
    """Load library config from JSON file. Accepts slug or canonical ID."""
    # Normalize: '/razorpay/razorpay-sdk' → 'razorpay'
    slug = library_id.lstrip("/").replace("/", "-").split("-")[0]
    full_slug = library_id.lstrip("/").replace("/", "-")

    # Try full slug first, then first-part slug
    for candidate in [full_slug, slug, library_id]:
        config_path = CONFIG_DIR / f"{candidate}.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)

    # Search all configs for matching library_id
    for config_file in CONFIG_DIR.glob("*.json"):
        with open(config_file) as f:
            config = json.load(f)
        if config.get("library_id") == library_id or config.get("library_id") == f"/{library_id}":
            return config

    raise ValueError(
        f"No config found for library: {library_id!r}. "
        f"Create backend/config/libraries/{slug}.json — see docs/CONTRIBUTING.md"
    )


async def _crawl(config: dict) -> list:
    """Dispatch to the correct crawler based on source type."""
    from app.ingestion.crawlers.web_crawler import RawDocument, WebCrawler
    from app.ingestion.crawlers.pdf_crawler import PDFCrawler
    from app.ingestion.crawlers.github_crawler import GitHubCrawler

    source = config.get("source", {})
    source_type = source.get("type", "web")
    lib_config = {**config, "library_id": config["library_id"]}

    if source_type == "web":
        urls = source.get("urls") or [source.get("url")]
        urls = [u for u in urls if u]
        return await WebCrawler().crawl(urls, lib_config)

    elif source_type == "pdf":
        urls = source.get("urls") or [source.get("url")]
        urls = [u for u in urls if u]
        return await PDFCrawler().crawl(urls, lib_config)

    elif source_type == "github":
        repos = source.get("repos") or [source.get("repo")]
        repos = [r for r in repos if r]
        return await GitHubCrawler(token=settings.GITHUB_TOKEN or None).crawl(repos, lib_config)

    elif source_type == "multi":
        all_docs = []
        for sub_source in source.get("sources", []):
            sub_config = {**lib_config, "source": sub_source}
            sub_docs = await _crawl(sub_config)
            all_docs.extend(sub_docs)
        return all_docs

    else:
        raise ValueError(f"Unknown source type: {source_type!r}")


async def _finalize_run(run_id, result: IngestionResult) -> None:
    """Update ingestion_run record with final status."""
    from app.core.database import AsyncSessionLocal
    from app.models.db import IngestionRun
    from sqlalchemy import select

    try:
        async with AsyncSessionLocal() as session:
            stmt = select(IngestionRun).where(IngestionRun.id == run_id)
            res = await session.execute(stmt)
            run = res.scalar_one_or_none()
            if run:
                run.status = result.status
                run.chunks_indexed = result.chunks_indexed
                run.chunks_deleted = result.chunks_deleted
                run.errors = result.errors
                run.completed_at = datetime.now(timezone.utc)
                run.duration_seconds = result.duration_seconds
                run.embedding_cost_usd = result.embedding_cost_usd
                await session.commit()
    except Exception as e:
        logger.warning(f"Failed to finalize run record: {e}")
