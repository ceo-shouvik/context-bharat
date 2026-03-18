#!/usr/bin/env python3
"""CLI: Test a search query against an indexed library."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def main():
    parser = argparse.ArgumentParser(description="Test search query against a library")
    parser.add_argument("--library", "-l", required=True, help="Library slug")
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--lang", default="en", help="Language (en, hi, ta, ...)")
    parser.add_argument("--tokens", type=int, default=5000, help="Max token budget")
    args = parser.parse_args()

    print(f"🔍 Query: '{args.query}'")
    print(f"📚 Library: {args.library}")
    print(f"🌐 Language: {args.lang}")
    print("-" * 60)

    from app.services.search_service import SearchService
    from app.models.schemas import Language
    service = SearchService()

    try:
        result = await service.query(
            library_id=f"/{args.library.replace('-', '/')}" if "/" not in args.library else args.library,
            query=args.query,
            token_budget=args.tokens,
            language=Language(args.lang),
        )
        if result:
            print(result.docs[:3000] + "..." if len(result.docs) > 3000 else result.docs)
            print(f"\n📊 Freshness: {result.freshness_score:.2f} | Sources: {result.sources}")
        else:
            print("❌ Library not found or not indexed yet")
    except NotImplementedError:
        print("⏳ SearchService not yet implemented — coming in Sprint 1")

if __name__ == "__main__":
    asyncio.run(main())
