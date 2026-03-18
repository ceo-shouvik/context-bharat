"""
Search service — hybrid BM25 + vector search with Cohere reranking.

Flow:
  1. Embed query  (OpenAI text-embedding-3-small)
  2. Vector search (pgvector cosine similarity, top 20)
  3. Keyword search (PostgreSQL full-text BM25, top 20)
  4. Merge + deduplicate (union of both sets)
  5. Rerank (Cohere Rerank v3, top N within token budget)
  6. Assemble response (Markdown, token-counted, with sources)

See knowledge-base/architecture.md#search-retrieval-flow for the spec.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.redis_client import get_cached, set_cached
from app.ingestion.embedder import embed_single
from app.models.schemas import Language, QueryDocsResponse
from app.repositories.library_repo import LibraryRepository
from app.repositories.vector_repo import SearchResult, VectorRepository

logger = logging.getLogger(__name__)

# Approximate tokens per word (conservative for code-heavy docs)
WORDS_PER_TOKEN = 0.75
RERANK_CANDIDATE_COUNT = 40  # Send top-N merged results to Cohere


@dataclass
class AssembledDoc:
    content: str
    token_count: int
    sources: list[str]


class SearchService:
    async def query(
        self,
        library_id: str,
        query: str,
        token_budget: int = 5000,
        language: Language = Language.EN,
    ) -> QueryDocsResponse | None:
        """
        Retrieve relevant docs for a library + query.
        Returns None if library not found in index.
        """
        async with AsyncSessionLocal() as session:
            return await self._query(session, library_id, query, token_budget, language)

    async def _query(
        self,
        session: AsyncSession,
        library_id: str,
        query: str,
        token_budget: int,
        language: Language,
    ) -> QueryDocsResponse | None:
        # 1. Verify library exists
        library_repo = LibraryRepository(session)
        library = await library_repo.get_by_id(library_id)
        if library is None:
            logger.warning(f"Library not found: {library_id}")
            return None

        # 2. Check cache
        import hashlib as _hashlib
        query_hash = _hashlib.sha256(query.encode()).hexdigest()[:12]
        cache_key = f"query:{library_id}:{language.value}:{query_hash}:{token_budget}"
        cached = await get_cached(cache_key)
        if cached:
            logger.debug(f"Cache hit: {cache_key}")
            import json
            data = json.loads(cached)
            return QueryDocsResponse(**data)

        vector_repo = VectorRepository(session)

        # 3. Embed query
        query_embedding = await embed_single(query)

        # 4. Parallel search: vector + keyword
        vector_results = await vector_repo.similarity_search(
            embedding=query_embedding,
            library_id=library_id,
            language=language.value,
            limit=20,
        )
        keyword_results = await vector_repo.keyword_search(
            query=query,
            library_id=library_id,
            language=language.value,
            limit=20,
        )

        # 5. Merge and deduplicate
        merged = _merge_results(vector_results, keyword_results, RERANK_CANDIDATE_COUNT)
        if not merged:
            logger.warning(f"No results for {library_id}: {query!r}")
            return QueryDocsResponse(
                docs=f"No documentation found for query: {query!r}",
                library_id=library_id,
                library_name=library.name,
                sources=[],
                freshness_score=library.freshness_score,
                language=language.value,
                token_count=0,
            )

        # 6. Rerank with Cohere
        reranked = await _rerank(query, merged)

        # 7. Assemble response within token budget
        assembled = _assemble_response(reranked, token_budget)

        response = QueryDocsResponse(
            docs=assembled.content,
            library_id=library_id,
            library_name=library.name,
            sources=assembled.sources,
            freshness_score=library.freshness_score,
            language=language.value,
            token_count=assembled.token_count,
        )

        # 8. Cache result for 5 minutes
        import json
        await set_cached(cache_key, json.dumps(response.model_dump()), ttl=300)

        return response


def _merge_results(
    vector_results: list[SearchResult],
    keyword_results: list[SearchResult],
    limit: int,
) -> list[SearchResult]:
    """
    Merge vector + keyword results. Deduplicate by chunk_id.
    Vector results score boosted slightly (semantic relevance preferred).
    """
    seen: dict[str, SearchResult] = {}

    for r in vector_results:
        seen[r.chunk_id] = SearchResult(
            chunk_id=r.chunk_id,
            library_id=r.library_id,
            content=r.content,
            url=r.url,
            section=r.section,
            language=r.language,
            score=r.score * 1.1,  # Slight boost for semantic match
        )

    for r in keyword_results:
        if r.chunk_id in seen:
            # Boost score for appearing in both
            existing = seen[r.chunk_id]
            seen[r.chunk_id] = SearchResult(
                chunk_id=existing.chunk_id,
                library_id=existing.library_id,
                content=existing.content,
                url=existing.url,
                section=existing.section,
                language=existing.language,
                score=existing.score + r.score * 0.5,
            )
        else:
            seen[r.chunk_id] = r

    return sorted(seen.values(), key=lambda r: r.score, reverse=True)[:limit]


async def _rerank(query: str, results: list[SearchResult]) -> list[SearchResult]:
    """
    Use Cohere Rerank v3 to re-score candidates.
    Falls back to original order if Cohere is unavailable.
    """
    if not settings.COHERE_API_KEY or not results:
        return results

    try:
        import cohere
        co = cohere.Client(settings.COHERE_API_KEY)

        documents = [r.content for r in results]
        response = co.rerank(
            model="rerank-v3.5",
            query=query,
            documents=documents,
            top_n=min(len(results), 20),
        )

        reranked = []
        for item in response.results:
            original = results[item.index]
            reranked.append(SearchResult(
                chunk_id=original.chunk_id,
                library_id=original.library_id,
                content=original.content,
                url=original.url,
                section=original.section,
                language=original.language,
                score=item.relevance_score,
            ))
        return reranked

    except Exception as e:
        logger.warning(f"Cohere rerank failed, using original order: {e}")
        return results


def _assemble_response(results: list[SearchResult], token_budget: int) -> AssembledDoc:
    """
    Assemble top results into a Markdown response within the token budget.
    Puts code-heavy chunks first (most useful for developers).
    """
    # Sort: code examples first, then guides, then references
    code_chunks = [r for r in results if "```" in r.content]
    other_chunks = [r for r in results if "```" not in r.content]
    ordered = code_chunks + other_chunks

    parts: list[str] = []
    sources: list[str] = []
    total_words = 0
    max_words = int(token_budget * WORDS_PER_TOKEN)

    for result in ordered:
        chunk_words = len(result.content.split())
        if total_words + chunk_words > max_words:
            break

        # Add section header if present
        if result.section and (not parts or result.section not in parts[-1]):
            parts.append(f"\n### {result.section}\n")

        parts.append(result.content)
        total_words += chunk_words

        if result.url and result.url not in sources:
            sources.append(result.url)

    content = "\n\n".join(p for p in parts if p.strip())
    token_estimate = int(total_words / WORDS_PER_TOKEN)

    return AssembledDoc(
        content=content or "No relevant documentation found.",
        token_count=token_estimate,
        sources=sources[:5],  # Cap source URLs to 5
    )
