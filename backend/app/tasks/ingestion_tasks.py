"""Celery tasks for asynchronous ingestion jobs."""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="app.tasks.ingestion_tasks.ingest_library",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    queue="ingestion",
)
def ingest_library(self, library_id: str, force: bool = False) -> dict:
    """
    Celery task: run full ingestion pipeline for one library.
    Retries up to 3 times with exponential backoff on failure.
    """
    import asyncio
    from app.ingestion.pipeline import run_ingestion

    logger.info(f"Starting ingestion task: {library_id} force={force}")
    try:
        result = asyncio.run(run_ingestion(library_id, force_refresh=force))
        logger.info(f"Ingestion complete: {library_id} chunks={result.chunks_indexed}")
        return {
            "library_id": library_id,
            "chunks_indexed": result.chunks_indexed,
            "status": "success",
        }
    except Exception as exc:
        logger.error(f"Ingestion failed: {library_id}", exc_info=exc)
        raise self.retry(exc=exc)


@shared_task(name="app.tasks.ingestion_tasks.scheduled_reindex_all")
def scheduled_reindex_all() -> dict:
    """
    Celery Beat task: triggered daily at 2 AM IST.
    Re-indexes all libraries past their refresh_interval_hours.
    """
    import json
    import os
    from pathlib import Path

    config_dir = Path(__file__).parent.parent.parent / "config" / "libraries"
    queued = []
    for config_file in config_dir.glob("*.json"):
        with open(config_file) as f:
            config = json.load(f)
        library_id = config.get("library_id", "").lstrip("/").replace("/", "-")
        ingest_library.apply_async(args=[library_id], queue="ingestion")
        queued.append(library_id)

    logger.info(f"Scheduled reindex queued {len(queued)} libraries")
    return {"queued": len(queued), "libraries": queued}
