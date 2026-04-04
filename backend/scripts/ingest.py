#!/usr/bin/env python3
"""CLI: Run ingestion pipeline for one or more libraries."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_all_library_ids() -> list[str]:
    config_dir = Path(__file__).parent.parent / "config" / "libraries"
    return [f.stem for f in sorted(config_dir.glob("*.json"))]


def get_library_ids_by_category(category: str) -> list[str]:
    config_dir = Path(__file__).parent.parent / "config" / "libraries"
    ids = []
    for f in sorted(config_dir.glob("*.json")):
        with open(f) as fp:
            config = json.load(fp)
        if config.get("category") == category:
            ids.append(f.stem)
    return ids


async def main():
    parser = argparse.ArgumentParser(description="Ingest library documentation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--library", "-l", help="Library slug (e.g. razorpay)")
    group.add_argument("--all", action="store_true", help="Ingest all libraries")
    group.add_argument("--category", "-c", help="Ingest by category")
    parser.add_argument("--force", "-f", action="store_true", help="Force re-index even if fresh")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview without writing to DB")

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN — no data will be written to the database")

    if args.all:
        library_ids = get_all_library_ids()
    elif args.category:
        library_ids = get_library_ids_by_category(args.category)
    else:
        library_ids = [args.library]

    print(f"📚 Queuing ingestion for {len(library_ids)} libraries: {library_ids}")

    for library_id in library_ids:
        print(f"\n▶ Starting: {library_id}")
        if not args.dry_run:
            from app.ingestion.pipeline import run_ingestion
            try:
                result = await run_ingestion(library_id, force_refresh=args.force)
                print(f"  ✅ Done: {result.chunks_indexed} chunks indexed")
                if result.errors:
                    print(f"  ⚠ {len(result.errors)} errors")
            except NotImplementedError:
                print(f"  ⏳ Pipeline not yet implemented — coming in Sprint 1")
            except Exception as e:
                print(f"  ❌ Failed: {e}")
        else:
            print(f"  [DRY RUN] Would ingest {library_id}")

if __name__ == "__main__":
    asyncio.run(main())
