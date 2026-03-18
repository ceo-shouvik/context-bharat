# System Architecture

Full technical architecture of Context7 India. Read this when you need to understand how all components connect.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Developer's AI Tool                          │
│         (Claude Desktop / Cursor / VS Code / Windsurf)          │
└────────────────────────┬────────────────────────────────────────┘
                         │ MCP Protocol (JSON-RPC 2.0)
                         │ stdio (local) OR Streamable HTTP (remote)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MCP Server (TypeScript)                        │
│                                                                 │
│  Tools:                                                         │
│  • resolve-library-id  → maps "razorpay" to /razorpay/sdk      │
│  • query-docs          → retrieves relevant doc chunks          │
│                                                                 │
│  Forked from: upstash/context7 (MIT License)                   │
│  Package: @context7india/mcp                                    │
│  Hosted: mcp.context7india.com (Cloudflare Worker)             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS REST API
                         │ Bearer token auth
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Backend API (Python / FastAPI)                     │
│                                                                 │
│  Routes:                                                        │
│  POST /v1/libraries/resolve  → library ID resolution           │
│  POST /v1/docs/query         → vector search + rerank          │
│  GET  /v1/libraries          → list all libraries              │
│  GET  /v1/libraries/{id}     → library metadata                │
│  POST /v1/keys               → API key management              │
│                                                                 │
│  Hosted: Railway (Singapore region)                             │
└─────────┬──────────────────────┬──────────────────────────────┘
          │                      │
          ▼                      ▼
┌──────────────────┐  ┌──────────────────────────────────────────┐
│  Redis (Upstash) │  │          Supabase (pgvector)              │
│                  │  │                                           │
│  • API response  │  │  Tables:                                  │
│    cache (5min)  │  │  • libraries (metadata, freshness)        │
│  • Rate limiting │  │  • doc_chunks (text + embedding vectors)  │
│  • Celery broker │  │  • api_keys (hashed, rate limits)         │
│                  │  │  • ingestion_runs (audit log)             │
│  Serverless      │  │  • users (Supabase Auth)                  │
└──────────────────┘  └────────────────────────────────────────┘
                                          ▲
                                          │ upsert vectors
                         ┌────────────────┴──────────────────────┐
                         │         Ingestion Pipeline             │
                         │         (Python / Celery)              │
                         │                                        │
                         │  1. Crawl   → Crawl4AI (web/GitHub)   │
                         │               PDFCrawler (Tesseract)   │
                         │               PortalCrawler (auth)     │
                         │                                        │
                         │  2. Extract → Markdown conversion      │
                         │               Table extraction          │
                         │               Code block detection      │
                         │                                        │
                         │  3. Chunk   → 512-token windows        │
                         │               Section boundary respect  │
                         │                                        │
                         │  4. Enrich  → LLM metadata tagging     │
                         │               Language detection        │
                         │               API category tagging      │
                         │                                        │
                         │  5. Embed   → OpenAI embedding API     │
                         │               text-embedding-3-small    │
                         │                                        │
                         │  6. Translate→ Sarvam AI Mayura        │
                         │               Hindi + regional langs    │
                         │                                        │
                         │  7. Upsert  → pgvector bulk insert      │
                         │               Hash-based dedup          │
                         │                                        │
                         │  Triggered by:                         │
                         │  • GitHub Actions daily cron           │
                         │  • Version bump webhook                │
                         │  • Admin manual trigger                │
                         │  • Community PR merge                  │
                         │                                        │
                         │  Hosted: Railway (separate worker)     │
                         └────────────────────────────────────────┘
```

---

## Component Details

### MCP Server

**Purpose:** The interface between AI coding assistants and our documentation index.

**What it does:**
- Implements MCP protocol (JSON-RPC 2.0) with stdio and Streamable HTTP transports
- Exposes `resolve-library-id` and `query-docs` tools
- Authenticates requests with API keys
- Calls the Backend API and formats responses for LLM consumption
- Handles token budgeting (default 5000 tokens per response)

**Key files:**
```
mcp-server/
├── src/
│   ├── index.ts          ← MCP server entrypoint
│   ├── tools/
│   │   ├── resolve-library-id.ts
│   │   └── query-docs.ts
│   ├── client.ts         ← Backend API HTTP client
│   └── config.ts         ← Environment + defaults
└── packages/sdk/         ← TypeScript SDK for programmatic access
```

**Deployment:**
- Remote: Cloudflare Worker at `mcp.context7india.com/mcp`
- Local: `npx @context7india/mcp` (stdio mode)
- Both modes share identical tool behavior

---

### Backend API

**Purpose:** Core business logic — search, retrieval, key management, ingestion orchestration.

**Key responsibilities:**
1. Library ID resolution (fuzzy name → canonical ID)
2. Hybrid search (BM25 + vector cosine similarity)
3. Reranking (Cohere cross-encoder)
4. Response assembly (merge chunks into token-budgeted response)
5. API key authentication and rate limiting
6. Ingestion job triggering via Celery

**Key files:**
```
backend/
├── app/
│   ├── main.py                    ← FastAPI app factory
│   ├── api/v1/
│   │   ├── libraries.py           ← Library search/resolve endpoints
│   │   ├── docs.py                ← Doc query endpoint
│   │   └── keys.py                ← API key CRUD
│   ├── services/
│   │   ├── search_service.py      ← Hybrid search + rerank logic
│   │   ├── library_service.py     ← Library metadata management
│   │   └── translation_service.py ← Sarvam AI integration
│   ├── ingestion/
│   │   ├── pipeline.py            ← Orchestrates full ingestion
│   │   ├── crawlers/
│   │   │   ├── web_crawler.py     ← Crawl4AI web crawling
│   │   │   ├── pdf_crawler.py     ← Tesseract + pdfplumber
│   │   │   ├── github_crawler.py  ← GitHub API + raw file access
│   │   │   └── portal_crawler.py  ← Auth + session crawling
│   │   ├── chunker.py             ← Token-aware document splitting
│   │   └── embedder.py            ← OpenAI embedding calls
│   ├── models/
│   │   ├── db.py                  ← SQLAlchemy models
│   │   └── schemas.py             ← Pydantic request/response schemas
│   └── tasks/
│       └── ingestion_tasks.py     ← Celery task definitions
├── config/
│   └── libraries/                 ← JSON config per library
├── scripts/
│   ├── ingest.py                  ← CLI: run ingestion for a library
│   ├── test_query.py              ← CLI: test search against indexed library
│   └── translate.py               ← CLI: trigger Hindi translation
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── alembic/                       ← DB migrations
```

---

### Database Schema

```sql
-- Core library metadata
CREATE TABLE libraries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    library_id      TEXT UNIQUE NOT NULL,  -- '/razorpay/razorpay-sdk'
    name            TEXT NOT NULL,
    description     TEXT,
    category        TEXT NOT NULL,         -- 'indian-fintech', 'india-dpi', etc.
    tags            TEXT[],
    npm_package     TEXT,
    pypi_package    TEXT,
    github_repo     TEXT,
    last_indexed_at TIMESTAMPTZ,
    freshness_score FLOAT,                 -- 0.0 to 1.0
    chunk_count     INTEGER DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Document chunks with vector embeddings
CREATE TABLE doc_chunks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    library_id  TEXT NOT NULL REFERENCES libraries(library_id),
    content     TEXT NOT NULL,             -- The actual doc text
    embedding   VECTOR(1536),             -- text-embedding-3-small dimensions
    url         TEXT,                      -- Source URL
    section     TEXT,                      -- Section heading
    language    TEXT DEFAULT 'en',         -- 'en', 'hi', 'ta', etc.
    content_hash TEXT,                     -- SHA256 for dedup
    metadata    JSONB DEFAULT '{}',        -- Flexible extra fields
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- pgvector index
CREATE INDEX idx_doc_chunks_embedding ON doc_chunks
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- API keys
CREATE TABLE api_keys (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES auth.users(id),
    key_hash    TEXT UNIQUE NOT NULL,      -- SHA256 of actual key
    key_prefix  TEXT NOT NULL,             -- First 8 chars for display
    name        TEXT,
    tier        TEXT DEFAULT 'free',       -- 'free', 'pro', 'team'
    daily_limit INTEGER DEFAULT 100,
    monthly_limit INTEGER DEFAULT 3000,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    is_active   BOOLEAN DEFAULT TRUE
);

-- Ingestion audit log
CREATE TABLE ingestion_runs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    library_id  TEXT NOT NULL,
    status      TEXT NOT NULL,            -- 'pending', 'running', 'success', 'failed'
    chunks_indexed INTEGER,
    errors      JSONB DEFAULT '[]',
    triggered_by TEXT,                    -- 'cron', 'version_bump', 'manual', 'pr'
    started_at  TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
```

---

### Search & Retrieval Flow

When a developer asks "how do I create a Razorpay payment link?":

```
1. MCP Tool: query-docs called with:
   - libraryId: "/razorpay/razorpay-sdk"
   - query: "create payment link"
   - tokenBudget: 5000

2. Backend API receives POST /v1/docs/query

3. Hybrid Search:
   a. BM25 keyword search on content TEXT column
      → returns top 20 by keyword relevance
   b. Embed the query: "create payment link"
      → 1536-dim vector via OpenAI
   c. pgvector cosine similarity search
      → returns top 20 by semantic similarity
   d. Merge results: union of both, deduplicated

4. Reranking:
   - Send top 40 merged chunks to Cohere Rerank v3
   - Returns ordered list of (chunk_id, relevance_score)
   - Select top N chunks within token budget

5. Response assembly:
   - Concatenate chunks in relevance order
   - Trim to tokenBudget (5000 tokens)
   - Include: content, urls, section names, freshness_score

6. MCP Server formats for LLM:
   - Returns structured Markdown with code examples at top
   - Includes source URLs as references
```

---

### Ingestion Pipeline Flow

When a library config is submitted or a cron triggers:

```
1. Celery task: run_ingestion(library_id="razorpay", force=False)

2. Load config from backend/config/libraries/razorpay.json

3. Check freshness:
   - If last_indexed_at < 24h ago and not force: skip
   - Update ingestion_runs record: status='running'

4. Crawl (source-type specific):
   Web: Crawl4AI → Playwright → extract Markdown
   PDF: pdfplumber (text PDF) OR Tesseract (scanned PDF)
   GitHub: GitHub API → raw Markdown files
   Multi: Combine all source types

5. Extract & Clean:
   - Remove navigation menus, footers, cookie banners
   - Preserve code blocks exactly
   - Extract tables → Markdown table format
   - Detect programming language of code blocks

6. Chunk:
   - Split at 512 tokens, respecting section boundaries
   - Each chunk tagged with: library_id, section, url, content_hash

7. Enrich (async LLM call, Claude Haiku):
   - Classify chunk: "API reference" | "guide" | "example" | "changelog"
   - Extract API endpoint if present
   - Language detection

8. Embed:
   - Batch API call to OpenAI text-embedding-3-small
   - 100 chunks per batch, 50% cost reduction

9. Translate (if library has non-English language config):
   - Sarvam AI Mayura for Hindi, Tamil, etc.
   - Creates parallel doc_chunks with language tag

10. Upsert:
    - For each chunk: if content_hash exists → update; else → insert
    - Bulk upsert for performance

11. Cleanup:
    - Delete doc_chunks for this library NOT in this run's hash set
      (removes deleted/renamed pages)
    - Update libraries: last_indexed_at, freshness_score, chunk_count
    - Update ingestion_runs: status='success', chunks_indexed=N
```

---

### Frontend Architecture

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx         ← Supabase Auth UI
│   │   └── signup/page.tsx
│   ├── (dashboard)/
│   │   ├── dashboard/page.tsx     ← Usage stats, API key management
│   │   ├── libraries/page.tsx     ← Browse all indexed libraries
│   │   └── libraries/[id]/page.tsx ← Individual library details + test query
│   ├── (public)/
│   │   ├── page.tsx               ← Landing page
│   │   └── docs/                  ← Getting started, MCP setup guides
│   └── api/
│       ├── keys/route.ts          ← API key CRUD
│       └── webhook/route.ts       ← Stripe webhooks (Pro billing)
├── components/
│   ├── ui/                        ← Shadcn/UI base components
│   ├── library-search.tsx         ← Real-time library search
│   ├── query-tester.tsx           ← Interactive doc query sandbox
│   └── usage-chart.tsx            ← Recharts usage analytics
└── lib/
    ├── supabase.ts                 ← Supabase client + server
    └── api.ts                      ← Backend API client
```

---

### Deployment Architecture

```
GitHub (source)
    │
    ├── Push to main
    │       │
    │       ├─→ GitHub Actions: test → build → deploy
    │       │
    │       ├─→ Railway: auto-deploys backend + Celery worker
    │       │
    │       └─→ Vercel: auto-deploys frontend
    │
    └── Daily cron (GitHub Actions, 2 AM IST)
            └─→ triggers Celery Beat → ingestion jobs for all libraries
```

### CDN / Edge

```
User Request → Cloudflare DNS
    │
    ├── api.context7india.com → Cloudflare Workers → Railway (origin)
    │   (5-min cache on GET /v1/libraries)
    │
    ├── mcp.context7india.com → Cloudflare Workers → MCP server
    │
    └── context7india.com → Vercel Edge Network → Next.js
```

---

## Scaling Path

| Scale | Vector DB | Compute | Cost/mo |
|-------|-----------|---------|---------|
| 0–5K users | pgvector (Supabase) | Railway hobby | ~$135 |
| 5K–50K users | pgvector (Supabase Pro) | Railway Pro | ~$500 |
| 50K–500K users | Qdrant Cloud | Railway + more workers | ~$3K |
| 500K+ users | Qdrant (self-hosted k8s) | AWS ECS | ~$15K |

Migration from pgvector to Qdrant: re-embed all chunks (one-time, ~$50 at current scale), swap `VectorRepository` implementation, update indexes.
