# Context Bharat — Claude Code Instructions

## Project Overview
Context Bharat is an AI-native MCP documentation server that indexes Indian fintech APIs, government APIs (UPI, GST, ONDC, Aadhaar), trading APIs (Zerodha, Upstox), enterprise tools (Zoho, Frappe, SAP B1), and global frameworks — serving India's 17M+ developers through Claude, Cursor, and VS Code via the Model Context Protocol.

**Think of this as:** A fork of Context7's open-source MCP client + a fully custom backend built for India's unique API landscape (PDFs, portal-gated docs, regional languages, offline-first).

---

## Quick Reference

### Essential commands
```bash
# Backend (Python — ingestion, API, vector DB)
cd backend && python -m uvicorn app.main:app --reload --port 8000
cd backend && python -m pytest tests/ -v
cd backend && python scripts/ingest.py --library razorpay --force

# MCP Server (TypeScript — forked from Context7)
cd mcp-server && pnpm dev
cd mcp-server && pnpm build && pnpm start
cd mcp-server && pnpm test

# Frontend (Next.js 15)
cd frontend && pnpm dev
cd frontend && pnpm build && pnpm start
cd frontend && pnpm test

# Full stack local
docker compose up -d           # Starts pgvector + Redis
pnpm run dev:all               # Starts all services concurrently
```

### Environment setup
```bash
cp .env.example .env           # Fill in secrets
pnpm install                   # Root workspace deps
cd backend && pip install -r requirements.txt
cd mcp-server && pnpm install
cd frontend && pnpm install
```

---

## Architecture at a Glance

```
Developer (Claude/Cursor/VS Code)
        ↓ MCP Protocol
  [MCP Server — TypeScript]       ← forked from upstash/context7
        ↓ REST
  [FastAPI Backend — Python]
     ↓              ↓
[pgvector DB]   [Redis Cache]
     ↑
[Ingestion Pipeline — Python]
  Crawl4AI + LlamaIndex + OCR
     ↑
[Source Docs: GitHub / npm / PDFs / Gov Portals]
```

Full architecture: @knowledge-base/architecture.md

---

## Monorepo Structure

```
context-bharat/
├── CLAUDE.md                    ← You are here
├── .claude/
│   ├── rules/                   ← Scoped rules by directory
│   └── commands/                ← Custom slash commands
├── backend/                     ← Python FastAPI + ingestion
│   ├── app/
│   │   ├── main.py              ← FastAPI entrypoint
│   │   ├── api/                 ← Route handlers
│   │   ├── ingestion/           ← Crawling + processing pipeline
│   │   ├── models/              ← SQLAlchemy + Pydantic models
│   │   └── services/            ← Business logic layer
│   ├── tests/
│   └── scripts/                 ← CLI tools (ingest, reindex, etc.)
├── mcp-server/                  ← TypeScript MCP server
│   ├── src/
│   │   ├── index.ts             ← MCP server entrypoint
│   │   ├── tools/               ← resolve-library-id, query-docs
│   │   └── client.ts            ← HTTP client for backend API
│   └── packages/sdk/            ← TypeScript SDK
├── frontend/                    ← Next.js 15 dashboard
│   ├── app/                     ← App Router pages
│   ├── components/              ← Shadcn/UI components
│   └── lib/                     ← Supabase client, utils
├── docs/                        ← Knowledge base (you are reading it)
├── knowledge-base/              ← Technical deep-dives
├── website/                     ← Marketing site content
├── docker-compose.yml
├── package.json                 ← Root pnpm workspace
└── .env.example
```

---

## Core Principles (Read This First)

See @docs/philosophy.md for the full philosophy. Summary:

1. **India-first, not India-only.** Our moat is Indian APIs. Global frameworks are table stakes.
2. **PDF is a first-class citizen.** Govt docs live in PDFs — our OCR pipeline must handle them gracefully.
3. **AI-native development.** Use Claude Code for boilerplate, tests, and integrations. Humans architect and review.
4. **Fresh docs always.** Daily cron re-crawls. Stale docs are worse than no docs.
5. **Offline-first for Tier 2/3.** Pre-downloadable packs. Sync-when-online.
6. **Open source the client, own the index.** MCP client = MIT. Backend = proprietary until we decide otherwise.

---

## Key Decisions Made

See @docs/decisions.md for full ADRs. Key choices:

| Decision | Choice | Why |
|---|---|---|
| Backend language | Python | LlamaIndex, Crawl4AI, ML tooling are Python-first |
| MCP server language | TypeScript | Ecosystem compatibility with Cursor/Claude |
| Vector DB (MVP) | pgvector on Supabase | One platform: DB + auth + storage. Free tier covers MVP |
| Vector DB (scale) | Qdrant | Rust-based, production-grade, complex metadata filtering |
| Crawling | Crawl4AI | 50k stars, handles JS-rendered pages, PDF+OCR, no API keys |
| Embeddings | text-embedding-3-small | Cheap ($0.02/1M tokens), fast, sufficient accuracy |
| Reranking | Cohere Rerank v3 | Best quality/cost. Fallback to cross-encoder local model |
| Hosting | Railway (backend) + Vercel (frontend) | Simplest managed infra for small team |
| Hindi translation | Sarvam AI Mayura | 22 Indian languages, purpose-built |
| Auth | Supabase Auth | Built-in with DB, OAuth, RLS policies |

---

## Domain Language

See @docs/domain-language.md for full glossary. Critical terms:

- **Library**: Any indexable doc source (API, SDK, framework, gov spec)
- **Library ID**: Canonical path like `/razorpay/razorpay-sdk` or `/npci/upi-specs`
- **Doc chunk**: A 512-token slice of documentation with metadata
- **Ingestion run**: One complete crawl-process-embed-upsert cycle for a library
- **India Stack**: The suite of government DPI APIs (UPI, Aadhaar, DigiLocker, ONDC, AA)
- **MCP Tool**: A function exposed by our MCP server (`resolve-library-id`, `query-docs`)
- **Token budget**: Max tokens returned per query-docs call (default 5000, configurable)
- **Freshness score**: How recently a library's docs were re-indexed (0-1 scale)

---

## Tech Stack

### Backend
- **Python 3.12** — runtime
- **FastAPI** — REST API framework
- **SQLAlchemy 2.0** — ORM (async)
- **pgvector** — vector similarity search
- **LlamaIndex** — document processing pipeline
- **Crawl4AI** — web crawling + PDF extraction
- **Tesseract + pytesseract** — OCR for scanned govt PDFs
- **Cohere** — reranking API
- **OpenAI** — text-embedding-3-small for embeddings
- **Sarvam AI** — Hindi + regional language translation
- **Redis (Upstash)** — response caching + rate limiting
- **Celery + Redis** — async task queue for ingestion jobs
- **pytest** — testing

### MCP Server
- **TypeScript / Node.js 20**
- **@modelcontextprotocol/typescript-sdk** — MCP protocol
- **zod** — schema validation
- **pnpm** — package manager

### Frontend
- **Next.js 15** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Shadcn/UI**
- **Supabase** (auth + DB client)
- **Recharts** — usage analytics
- **pnpm**

### Infrastructure
- **Supabase** — PostgreSQL + pgvector + Auth + Storage
- **Railway** — Python backend + Celery workers
- **Vercel** — Next.js frontend
- **Cloudflare** — DNS + CDN + Workers for edge caching
- **Upstash Redis** — serverless Redis
- **GitHub Actions** — CI/CD + daily ingestion cron

---

## Development Workflow

See @docs/design-patterns.md for patterns. Standard flow:

1. **Plan first** — before writing code, describe the feature and let Claude Code generate a task spec
2. **Write the test** — tests go in `tests/` mirroring the source structure
3. **Implement** — keep functions small (<50 lines), single responsibility
4. **Document** — update the relevant knowledge-base file if you add a new system component
5. **PR** — follow @docs/CONTRIBUTING.md

### Git conventions
```
feat/ingestion-ocr-pipeline
fix/mcp-resolve-library-timeout
docs/add-gstn-api-guide
chore/update-dependencies
```

Commit format: `type(scope): description` — e.g. `feat(ingestion): add PDF OCR pipeline for govt docs`

---

## Common Tasks

### Add a new library to the index
1. Create `knowledge-base/libraries/<library-name>.md` following the template in @knowledge-base/api-catalog.md
2. Add `context7.json` config entry in `backend/config/libraries/`
3. Run `python scripts/ingest.py --library <name> --dry-run` to preview
4. Run `python scripts/ingest.py --library <name>` to index
5. Verify: `python scripts/test_query.py --library <name> --query "authentication"`

### Run ingestion for all Indian fintech APIs
```bash
python scripts/ingest.py --category indian-fintech
```

### Add a translation for a library
```bash
python scripts/translate.py --library razorpay --lang hi  # Hindi
python scripts/translate.py --library razorpay --lang ta  # Tamil
```

### Test MCP tools locally
```bash
# In mcp-server/
npx @modelcontextprotocol/inspector dist/index.js
```

---

## Environment Variables

See `.env.example` for all variables. Critical ones:
```
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
OPENAI_API_KEY=               # For embeddings
COHERE_API_KEY=               # For reranking
SARVAM_API_KEY=               # For Hindi translation
UPSTASH_REDIS_URL=
UPSTASH_REDIS_TOKEN=
RAILWAY_API_KEY=              # For deployment
CONTEXT7_API_BASE_URL=        # Our backend API URL (for MCP server)
```

---

## Testing Strategy

- **Unit tests** — `pytest tests/unit/` — pure functions, no I/O
- **Integration tests** — `pytest tests/integration/` — real DB, needs local stack
- **E2E tests** — `pytest tests/e2e/` — full ingestion + query cycle
- **MCP tests** — `pnpm test` in mcp-server/ — tool call contract tests

Run before every PR: `make test` (runs unit + integration)

---

## References

- @docs/philosophy.md — Why we build the way we build
- @docs/decisions.md — Architecture Decision Records (ADRs)
- @docs/design-patterns.md — Code patterns and conventions
- @docs/domain-language.md — Glossary of domain terms
- @docs/style-guide.md — Code style and formatting rules
- @knowledge-base/architecture.md — Full system architecture
- @knowledge-base/ingestion-pipeline.md — How crawling + indexing works
- @knowledge-base/mcp-server.md — MCP server implementation details
- @knowledge-base/api-catalog.md — All supported libraries and their status
- @knowledge-base/infra.md — Infrastructure setup and costs
- @knowledge-base/roadmap.md — What we're building next
- @website/content.md — Marketing site copy and messaging
