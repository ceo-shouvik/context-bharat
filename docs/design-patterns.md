# Design Patterns

Patterns we use consistently across the codebase. When in doubt, follow the pattern here rather than inventing a new one.

---

## Backend Patterns (Python)

### API Route Handler Pattern

Every route handler is thin — it validates input, calls a service, returns output. No business logic in handlers.

```python
# backend/app/api/v1/libraries.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.library_service import LibraryService
from app.models.schemas import LibrarySearchRequest, LibrarySearchResponse
from app.dependencies import get_library_service

router = APIRouter(prefix="/libraries", tags=["libraries"])

@router.get("/search", response_model=LibrarySearchResponse)
async def search_libraries(
    query: str,
    limit: int = 10,
    service: LibraryService = Depends(get_library_service),
) -> LibrarySearchResponse:
    """Search libraries by name or description."""
    results = await service.search(query=query, limit=limit)
    return LibrarySearchResponse(results=results, count=len(results))
```

### Service Layer Pattern

Business logic lives in services. Services are injected via FastAPI's `Depends()`.

```python
# backend/app/services/library_service.py
from app.repositories.library_repo import LibraryRepository
from app.repositories.vector_repo import VectorRepository

class LibraryService:
    def __init__(
        self,
        library_repo: LibraryRepository,
        vector_repo: VectorRepository,
    ):
        self._library_repo = library_repo
        self._vector_repo = vector_repo

    async def search(self, query: str, limit: int = 10) -> list[LibraryResult]:
        # 1. Text search in library metadata
        candidates = await self._library_repo.search_by_name(query)
        # 2. Semantic search in vector store
        semantic = await self._vector_repo.search(query, limit=limit * 2)
        # 3. Merge and rerank
        return self._merge_results(candidates, semantic, limit)
```

### Repository Pattern

Database access is encapsulated in repositories. Never write SQL in services or handlers.

```python
# backend/app/repositories/library_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.db import Library

class LibraryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, library_id: str) -> Library | None:
        result = await self._session.execute(
            select(Library).where(Library.library_id == library_id)
        )
        return result.scalar_one_or_none()

    async def search_by_name(self, query: str) -> list[Library]:
        result = await self._session.execute(
            select(Library).where(Library.name.ilike(f"%{query}%"))
        )
        return result.scalars().all()
```

### Ingestion Pipeline Pattern

Each library ingestion follows the same pipeline stages. New source types implement the `BaseCrawler` interface.

```python
# backend/app/ingestion/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class RawDocument:
    url: str
    content: str
    content_type: str  # "markdown" | "html" | "pdf"
    metadata: dict

class BaseCrawler(ABC):
    @abstractmethod
    async def crawl(self, library_id: str, config: dict) -> list[RawDocument]:
        """Crawl source and return raw documents."""
        ...

# Usage in pipeline:
async def run_ingestion(library_id: str):
    config = load_config(library_id)
    crawler = get_crawler(config["source_type"])  # GitHubCrawler | PDFCrawler | WebCrawler

    raw_docs = await crawler.crawl(library_id, config)
    chunks = chunk_documents(raw_docs)           # Split into 512-token chunks
    enriched = await enrich_chunks(chunks)        # LLM metadata tagging
    embeddings = await embed_chunks(enriched)     # OpenAI embeddings
    await upsert_vectors(library_id, embeddings)  # pgvector upsert
    await update_library_metadata(library_id)     # freshness timestamp
```

### Error Handling Pattern

```python
# Always use specific exceptions, never bare except
from app.exceptions import LibraryNotFoundError, IngestionError

try:
    result = await service.get_library(library_id)
except LibraryNotFoundError:
    raise HTTPException(status_code=404, detail=f"Library {library_id} not found")
except IngestionError as e:
    logger.error(f"Ingestion failed for {library_id}", exc_info=e)
    raise HTTPException(status_code=500, detail="Ingestion failed")
```

### Async Pattern

All I/O operations must be async. No blocking calls in async functions.

```python
# Good
async def fetch_doc(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

# Bad — blocks the event loop
def fetch_doc(url: str) -> str:
    import requests
    return requests.get(url).text
```

---

## TypeScript / MCP Server Patterns

### Tool Definition Pattern

Each MCP tool is a self-contained module with input schema + handler.

```typescript
// mcp-server/src/tools/query-docs.ts
import { z } from "zod";
import { Tool } from "@modelcontextprotocol/typescript-sdk";
import { backendClient } from "../client";

const QueryDocsInput = z.object({
  libraryId: z.string().describe("Context7India-compatible library ID, e.g. /razorpay/razorpay-sdk"),
  query: z.string().describe("The developer's question or task"),
  tokenBudget: z.number().default(5000).describe("Max tokens in response"),
  language: z.enum(["en", "hi", "ta", "te", "kn", "bn"]).default("en"),
});

export const queryDocsTool: Tool = {
  name: "query-docs",
  description: "Retrieve documentation for a library. Supports Indian APIs, government specs, and global frameworks. Specify language for Hindi/regional docs.",
  inputSchema: QueryDocsInput,
  async handler(input) {
    const result = await backendClient.getDocs({
      libraryId: input.libraryId,
      query: input.query,
      maxTokens: input.tokenBudget,
      language: input.language,
    });
    return { content: result.docs, freshness: result.freshnessScore };
  },
};
```

### HTTP Client Pattern

```typescript
// mcp-server/src/client.ts
class BackendClient {
  private readonly baseUrl: string;
  private readonly apiKey: string | undefined;

  constructor() {
    this.baseUrl = process.env.CONTEXT7INDIA_API_BASE_URL ?? "https://api.context7india.com";
    this.apiKey = process.env.CONTEXT7INDIA_API_KEY;
  }

  async getDocs(params: GetDocsParams): Promise<DocsResponse> {
    const response = await fetch(`${this.baseUrl}/v1/docs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(this.apiKey ? { "Authorization": `Bearer ${this.apiKey}` } : {}),
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
}

export const backendClient = new BackendClient();
```

---

## Frontend Patterns (Next.js 15)

### Server Component Pattern

Default to Server Components. Use Client Components only for interactivity.

```typescript
// frontend/app/library/[id]/page.tsx — Server Component
import { getLibrary } from "@/lib/api";

export default async function LibraryPage({ params }: { params: { id: string } }) {
  const library = await getLibrary(params.id);  // Runs on server

  return (
    <div>
      <LibraryHeader library={library} />
      <DocViewer docs={library.docs} />  {/* Client Component for search */}
    </div>
  );
}
```

### API Route Pattern

```typescript
// frontend/app/api/keys/route.ts
import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export async function POST(request: Request) {
  const supabase = createRouteHandlerClient({ cookies });
  const { data: { session } } = await supabase.auth.getSession();

  if (!session) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Create API key logic...
  return Response.json({ key: newKey }, { status: 201 });
}
```

---

## Testing Patterns

### Unit Test Pattern (Python)

```python
# backend/tests/unit/test_chunker.py
import pytest
from app.ingestion.chunker import chunk_document

def test_chunk_respects_token_limit():
    long_doc = "word " * 10000
    chunks = chunk_document(long_doc, max_tokens=512)
    assert all(len(c.content.split()) <= 512 for c in chunks)

def test_chunk_preserves_markdown_sections():
    doc = "# Section 1\nContent 1\n# Section 2\nContent 2"
    chunks = chunk_document(doc, max_tokens=512)
    # Section headers should start new chunks
    assert chunks[0].content.startswith("# Section 1")
```

### Integration Test Pattern (Python)

```python
# backend/tests/integration/test_search_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_search_returns_razorpay_for_payment_query(test_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/libraries/search?query=razorpay payment india")
    assert response.status_code == 200
    data = response.json()
    assert any("razorpay" in r["library_id"] for r in data["results"])
```

---

## Configuration Pattern

Library ingestion configs live in `backend/config/libraries/`. One JSON file per library.

```json
// backend/config/libraries/razorpay.json
{
  "library_id": "/razorpay/razorpay-sdk",
  "name": "Razorpay",
  "description": "India's leading payment gateway. Payment links, orders, subscriptions, payouts, and webhooks.",
  "category": "indian-fintech",
  "source": {
    "type": "web",
    "urls": [
      "https://razorpay.com/docs/",
      "https://razorpay.com/docs/api/"
    ],
    "crawl_depth": 3
  },
  "npm_package": "razorpay",
  "pypi_package": "razorpay",
  "github_repo": "razorpay/razorpay-node",
  "refresh_interval_hours": 24,
  "languages": ["en", "hi"],
  "tags": ["payments", "india", "fintech", "upi", "subscription"]
}
```

```json
// backend/config/libraries/ondc-protocol.json
{
  "library_id": "/ondc/protocol-specs",
  "name": "ONDC Protocol",
  "description": "Open Network for Digital Commerce. Beckn Protocol implementation for buyer/seller apps.",
  "category": "india-dpi",
  "source": {
    "type": "multi",
    "sources": [
      { "type": "github", "repo": "ONDC-Official/ONDC-Protocol-Specs" },
      { "type": "github", "repo": "ONDC-Official/log-validation-utility" },
      { "type": "web", "url": "https://docs.ondc.org/", "crawl_depth": 4 },
      { "type": "pdf", "url": "https://ondc.org/wp-content/uploads/2023/ondc-api-contract.pdf" }
    ]
  },
  "refresh_interval_hours": 48,
  "languages": ["en", "hi"],
  "tags": ["ondc", "beckn", "ecommerce", "india", "dpi"]
}
```

---

## Naming Conventions

### Python
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Type aliases: `PascalCase`

### TypeScript
- Files: `kebab-case.ts`
- Classes: `PascalCase`
- Functions: `camelCase`
- Constants: `UPPER_SNAKE_CASE` or `camelCase` for config objects
- Types/interfaces: `PascalCase`

### Database
- Tables: `snake_case` plural (`libraries`, `doc_chunks`, `api_keys`)
- Columns: `snake_case` (`library_id`, `created_at`, `freshness_score`)
- Indexes: `idx_{table}_{column}` (`idx_libraries_category`)

### API Endpoints
- REST: `/v1/{resource}/{action}` — plural resources, lowercase, hyphens
- `/v1/libraries/search`
- `/v1/docs/query`
- `/v1/keys/generate`

### Library IDs
- Format: `/{owner}/{repo}` (mirrors Context7 convention for compatibility)
- Indian fintech: `/razorpay/razorpay-sdk`, `/cashfree/cashfree-pg`
- Indian DPI: `/npci/upi-specs`, `/ondc/protocol-specs`, `/gstn/gst-api`
- Indian trading: `/zerodha/kite-api`, `/upstox/upstox-api`
- Enterprise: `/zoho/zoho-crm`, `/frappe/frappe-framework`
