#!/usr/bin/env python3
"""GitHub Actions: Trigger scheduled re-indexing via Celery."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    from app.tasks.ingestion_tasks import scheduled_reindex_all
    print("🔄 Triggering scheduled re-index...")
    result = scheduled_reindex_all.apply_async()
    print(f"✅ Task queued: {result.id}")
    print(f"📚 Libraries queued: {result.get(timeout=10)}")
