"""Celery application factory."""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "context7india",
    broker=settings.UPSTASH_REDIS_URL,
    backend=settings.UPSTASH_REDIS_URL,
    include=["app.tasks.ingestion_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Run tasks inline in tests
    task_always_eager=False,
)

# Beat schedule — daily re-index at 2 AM IST (20:30 UTC)
celery_app.conf.beat_schedule = {
    "daily-reindex-all": {
        "task": "app.tasks.ingestion_tasks.scheduled_reindex_all",
        "schedule": crontab(hour=20, minute=30),
        "options": {"queue": "ingestion"},
    },
}
