# Architecture Decision Records (ADRs)

Permanent record of every significant technical decision. Add new ADRs at the bottom. Never edit old ones — add a superseding ADR instead.

Format: Context → Decision → Consequences → Status

---

## ADR-001: Fork Context7 MCP Client Rather Than Build From Scratch

**Date:** March 2026
**Status:** Accepted

**Context:**
The MCP (Model Context Protocol) is a complex JSON-RPC 2.0 specification with multiple transport modes (stdio, Streamable HTTP), tool definitions, schema validation, and multi-client compatibility requirements. Building this from scratch would take 6–8 weeks.

Context7's repo (`upstash/context7`) is MIT-licensed. It contains the MCP client layer: TypeScript SDK, tool definitions (`resolve-library-id`, `query-docs`), transport handling, and multi-editor integration configs. Their backend (crawling, vector DB, ranking) is proprietary and not included.

**Decision:**
Fork `upstash/context7` at the MCP client layer. Keep our own backend entirely separate. Rename the npm package to `@contextbharat/mcp`. Update the API base URL to point to our backend. Add our India-specific tool extensions on top.

**Consequences:**
- Saves 6 weeks of MCP protocol implementation
- We receive upstream improvements by watching the fork
- We must maintain compatibility with new MCP spec versions
- Risk: if Context7 changes license (unlikely — MIT is irrevocable for past commits)
- We clearly document that we forked and credit Upstash

---

## ADR-002: Python for Backend, TypeScript for MCP Server

**Date:** March 2026
**Status:** Accepted

**Context:**
Two components have different optimal language choices. The ingestion pipeline needs ML/AI libraries. The MCP server needs to match the ecosystem.

**Decision:**
- **Backend (ingestion + REST API):** Python 3.12. Reasons: LlamaIndex, Crawl4AI, Tesseract, Cohere, and OpenAI SDKs are all Python-first. Fastest path to a working ingestion pipeline.
- **MCP Server:** TypeScript. Reasons: `@modelcontextprotocol/typescript-sdk` is the reference implementation. Cursor, Claude Desktop, and VS Code plugins are JS/TS ecosystems. Forked code is already TypeScript.

**Consequences:**
- Two language runtimes to maintain
- Different testing frameworks (pytest vs jest/vitest)
- Engineers need to be comfortable with both (or we split ownership)
- No shared code between services (intentional — they communicate via REST)

---

## ADR-003: pgvector on Supabase for MVP, Qdrant for Scale

**Date:** March 2026
**Status:** Accepted

**Context:**
We need vector similarity search for doc retrieval. Options: Pinecone (expensive, proprietary), Weaviate (complex), Qdrant (excellent but separate infra), pgvector (Postgres extension).

**Decision:**
MVP uses **pgvector on Supabase**. Reasons:
- Supabase gives us Postgres + pgvector + Auth + Storage + Realtime in one platform
- Free tier: 500MB DB, 1GB storage — enough for MVP with ~5M vectors
- We already need Postgres for relational data (libraries, API keys, users)
- Zero additional infrastructure to manage

Migration to **Qdrant** when: we exceed Supabase limits, or need advanced filtering, or require higher throughput. Qdrant is Rust-based, production-grade, and supports complex metadata filters we'll eventually need.

**Consequences:**
- MVP is simpler and cheaper
- Migration to Qdrant requires embedding migration (we keep original vectors)
- pgvector's ANN algorithm (IVFFlat) is slower than Qdrant's HNSW at scale
- We abstract vector operations behind a `VectorStore` interface so migration is a swap

---

## ADR-004: Crawl4AI for Web Crawling, Tesseract for PDF OCR

**Date:** March 2026
**Status:** Accepted

**Context:**
Indian government APIs present unique ingestion challenges:
- Many docs are PDFs (including scanned image PDFs)
- Some portals require authentication and session management
- Some pages are JavaScript-rendered SPAs (ABDM sandbox)
- Rate limiting and anti-bot measures on government portals

**Decision:**
- **Crawl4AI** for web crawling: 50k+ GitHub stars, handles JS-rendered pages via Playwright, supports session/cookie management for authenticated portals, outputs LLM-ready Markdown, built-in PDF extraction, no API keys required
- **Tesseract + pytesseract** for image-based PDF OCR: open-source, handles Hindi text (Sanskrit/Devanagari script), integrates with pdf2image for preprocessing
- **pdfplumber** for text-based PDFs: better than PyMuPDF for table extraction, which is critical for API parameter tables in government specs
- **Firecrawl** as fallback: for sites that block Crawl4AI, we use Firecrawl's API (AGPL-3.0)

**Consequences:**
- Playwright dependency adds ~100MB to container image
- Tesseract requires system-level installation in Docker
- OCR quality varies by scan quality — we store confidence scores
- We need a human review queue for low-confidence OCR extractions

---

## ADR-005: OpenAI text-embedding-3-small for Embeddings

**Date:** March 2026
**Status:** Accepted

**Context:**
Embedding model choice affects: cost, latency, quality, and vendor lock-in.

**Decision:**
**text-embedding-3-small** from OpenAI. Reasons:
- $0.02/1M tokens — cheapest quality embedding model available
- 1536 dimensions — sufficient for documentation retrieval tasks
- Natively handles code snippets and technical terminology
- Batch API available for bulk ingestion (50% cost reduction)

We evaluated: `bge-m3` (local, multilingual but slow), `e5-mistral-7b` (too large), Cohere Embed v3 (good but expensive), `text-embedding-3-large` (better quality but 4× cost).

**Consequences:**
- Vendor dependency on OpenAI for embeddings
- If OpenAI changes pricing or availability, we need to re-embed (~$50 one-time cost at current scale)
- Fallback: `sentence-transformers/all-MiniLM-L6-v2` local model if OpenAI is unavailable
- Hindi text embedding quality is acceptable but not optimal — we track retrieval quality per language

---

## ADR-006: Sarvam AI for Indian Language Translation

**Date:** March 2026
**Status:** Accepted

**Context:**
We want to provide documentation in Hindi and 4 other Indian regional languages. Options: Google Translate API (good but generic, not tech-tuned), DeepL (no Indian language support), Bhashini (government, free but rate-limited and unreliable), Sarvam AI Mayura.

**Decision:**
**Sarvam AI Mayura** as primary translation API. Reasons:
- Purpose-built for Indian languages by ex-AI4Bharat researchers
- 22 Indian languages supported
- Technical terminology handling is better than Google Translate
- $41M raised from Lightspeed + Peak XV — reliable vendor
- Startup program: 6–12 months free API credits (we applied)

**Bhashini** as fallback for PoC and rate-limit overflow (free, government-backed).

**Consequences:**
- Per-character cost for translations (budget: $15–40/month at MVP scale)
- Translation quality requires human review for technical accuracy
- We do not translate code samples — only prose documentation
- Technical terms (API, SDK, endpoint, webhook) kept in English with Hindi parenthetical

---

## ADR-007: Railway for Backend Hosting

**Date:** March 2026
**Status:** Accepted

**Context:**
We need managed hosting for the Python FastAPI backend and Celery workers. Options: AWS ECS (complex, expensive), Fly.io (good DX, limited India regions), Render (simple but less control), Railway (simplest, great DX), Heroku (expensive).

**Decision:**
**Railway** for all Python services. Reasons:
- $5/month hobby → $20/month production (predictable cost)
- Native support for Celery workers as separate services
- GitHub Actions integration for auto-deploy
- Environment variable management built-in
- No server configuration required
- Singapore region available (lowest latency for Indian users)

**Consequences:**
- Less control than ECS/Kubernetes (acceptable for MVP)
- Scale ceiling: Railway can handle ~1000 RPS per service (sufficient for our scale)
- Migration path: When Railway becomes the bottleneck, containerize and move to AWS ECS or Fly.io
- Vendor lock-in is low — we use standard Docker containers

---

## ADR-008: Apache 2.0 for Open-Source Components

**Date:** March 2026
**Status:** Accepted

**Context:**
We need to decide what to open-source and under what license. The community model (like Context7) relies on community contributions to add libraries.

**Decision:**
- **MCP Server client layer:** Apache 2.0 (permissive, allows commercial use by integrators)
- **Library config schema (`contextbharat.json` format):** Public domain / CC0
- **Backend ingestion pipeline:** **Proprietary / closed** — this is our moat
- **Vector index and embeddings:** **Proprietary / closed**

We accept community PRs for:
- Adding new library configs (JSON files only, no backend code)
- Improving MCP client code
- Documentation improvements

**Consequences:**
- Community can extend MCP client without contributing to our backend
- Library config PRs give us crowdsourced library discovery
- We cannot prevent forks of our MCP client (acceptable — value is in the index)
- Clearly different from Context7's "open-source washing" stance

---

## ADR-009: Celery + Redis for Async Ingestion Jobs

**Date:** March 2026
**Status:** Accepted

**Context:**
Ingestion jobs (crawling + embedding + upserting 100+ libraries) are long-running background tasks that cannot run synchronously in an HTTP request.

**Decision:**
**Celery** with **Upstash Redis** as broker and result backend. Reasons:
- Industry standard for Python async tasks
- Retry logic built-in (critical for flaky gov portal crawls)
- Priority queues: high-priority re-index on version bump, low-priority daily refresh
- Beat scheduler for cron jobs (daily re-index)
- Upstash Redis is serverless, no instance to manage, free tier covers our needs

**Consequences:**
- Additional service to run (Celery worker)
- Redis dependency (already needed for API caching)
- Flower dashboard for monitoring (optional but recommended)
- In tests, tasks run eagerly (`CELERY_TASK_ALWAYS_EAGER=True`)

---

## ADR-010: Pay-Per-Use Credits Over Subscriptions

**Date:** March 2026
**Status:** Accepted

**Context:**
Original pricing was subscription-based (Free / ₹399 Pro / ₹999 Team per month). Indian developers are subscription-fatigued and price-sensitive. Casual users (majority of early adopters) won't commit ₹399/month for occasional use. Industry trend (Anthropic, OpenAI, Upstash) is moving toward usage-based billing.

**Decision:**
Adopt **prepaid credit packs** (Anthropic-style) instead of subscriptions:
- Free tier: 200 credits/day with account (50 without)
- Credit packs: ₹99 (5K credits) → ₹3,999 (500K credits)
- 1 query = 1 credit (simple, predictable)
- Credits never expire (competitive advantage)
- Implement with Razorpay (India) + Stripe (international) + DIY ledger in Supabase

**Consequences:**
- Lower barrier to entry — ₹99 starter pack vs ₹399/mo subscription
- Revenue less predictable but scales with actual usage
- Need to build credit ledger + metering (2 weeks of work)
- Most users won't use 100% of credits → profitable at ~40-60% utilization
- Can add hybrid "monthly auto-refill" plan later if needed
- Full pricing strategy: see `docs/pricing-strategy.md`

---

## ADR-011: Open-Source vs Private Repository Split

**Date:** March 2026
**Status:** Accepted

**Context:**
We need to decide what code lives in the public GitHub repo (drives adoption, community, SEO, trust) vs what stays in a private Bitbucket repo (protects moat, proprietary logic, business secrets). The split must balance maximum community value with protecting competitive advantage.

Key principles from our philosophy:
- "Open-source the client, own the index" (ADR-008)
- Free setup tools drive traffic at zero infra cost
- Community contributions (library configs) are a growth lever
- The ingestion pipeline, vector index, and ranking are our moat

**Decision:**

### PUBLIC — GitHub (`github.com/contextbharat/context-bharat`)

Everything a developer needs to **use** Context Bharat or **contribute** library configs:

| Component | Why Public |
|-----------|-----------|
| `mcp-server/` | Apache 2.0 MCP client — community can extend, fork, build integrations |
| `tools/` | Setup scripts (GitHub MCP, Context Bharat, MCP Doctor) — zero-cost traffic driver, SEO magnet |
| `frontend/app/(public)/` | Public pages: landing, docs, setup guides, pricing — marketing + SEO |
| `frontend/app/setup/` | Setup tool pages — the whole point is discoverability |
| `frontend/components/live-playground.tsx` | Demo component — lets developers try before signup |
| `frontend/components/logo-slider.tsx` | Marketing component |
| `docs/` | Philosophy, decisions, contributing guide, style guide — attracts contributors |
| `knowledge-base/api-catalog.md` | Library catalog — community PRs to add new libraries |
| `knowledge-base/mcp-server.md` | MCP server docs — helps integrators |
| `backend/config/libraries/` | Library JSON configs — the community contribution target |
| `backend/app/ingestion/base.py` | BaseCrawler interface — so community knows the contract |
| `docker-compose.yml` | Local dev setup |
| `Makefile` | Developer commands |
| `.env.example` | Environment template |
| `CLAUDE.md` | Claude Code instructions |
| `README.md` | Project overview |
| `website/` | Marketing copy source of truth |

### PRIVATE — Bitbucket (`bitbucket.org/contextbharat/context-bharat-private`)

Everything that is our **competitive moat** or contains **business secrets**:

| Component | Why Private |
|-----------|------------|
| `backend/app/ingestion/pipeline.py` | Full ingestion orchestration — our core IP |
| `backend/app/ingestion/crawlers/` | All crawler implementations (web, PDF, GitHub, portal) — hard-won logic for govt portals, OCR tuning |
| `backend/app/ingestion/chunker.py` | Token-aware chunking with section boundary logic |
| `backend/app/ingestion/embedder.py` | Embedding batch strategy, cost optimizations |
| `backend/app/services/search_service.py` | Hybrid search + reranking algorithm — the ranking quality is our moat |
| `backend/app/services/translation_service.py` | Sarvam AI integration, term preservation logic |
| `backend/app/api/v1/` | API route handlers (thin, but reveals exact API behavior) |
| `backend/app/repositories/` | Database access patterns, query optimizations |
| `backend/app/tasks/` | Celery task definitions, retry logic for flaky govt portals |
| `backend/app/core/config.py` | Internal config with all env var handling |
| `backend/scripts/ingest.py` | CLI ingestion tool |
| `backend/scripts/translate.py` | Translation CLI |
| `backend/tests/` | Test suite — reveals internal implementation details |
| `backend/alembic/` | DB migrations — reveals exact schema evolution |
| `frontend/app/(dashboard)/` | Dashboard pages — reveals our product analytics, admin features |
| `frontend/app/(auth)/` | Auth flow implementation |
| `frontend/app/api/` | Internal API routes |
| `frontend/components/api-key-manager.tsx` | Key management UI |
| `frontend/components/usage-chart.tsx` | Usage analytics |
| `frontend/components/query-tester.tsx` | Dashboard query sandbox (different from public demo) |
| `frontend/lib/supabase.ts` | Supabase client config |
| `frontend/lib/admin-api.ts` | Admin API client |
| `frontend/app/admin/` | Full admin dashboard |
| `knowledge-base/architecture.md` | Full system architecture with infra details |
| `knowledge-base/infra.md` | Infrastructure setup, costs, secrets |
| `knowledge-base/roadmap.md` | Detailed sprint plans and timelines |
| `docs/pricing-strategy.md` | Detailed pricing model and margins |
| `docs/deployment-plan.md` | Deployment infrastructure details |
| `.github/workflows/` | CI/CD pipelines — reveals deploy targets, secrets structure |

### SHARED — Exists in both, synced manually

| File | Notes |
|------|-------|
| `backend/app/models/schemas.py` | Pydantic schemas — public for SDK builders, private for full implementation |
| `backend/app/models/db.py` | DB models — public shows table structure (already in architecture docs), private has full implementation |

**Consequences:**
- Public repo is the "storefront" — clean, documented, welcoming to contributors
- Private repo has the full working codebase — deployed from Bitbucket
- Community PRs land on GitHub (library configs only), manually synced to Bitbucket
- Setup tools are fully public — maximum discoverability and SEO
- We never accidentally expose API keys, infra costs, or admin dashboard code
- Two repos to maintain — use CI on Bitbucket for deploys, GitHub for community

---

## ADR-012: Free Setup Tools as Growth Strategy

**Date:** March 2026
**Status:** Accepted

**Context:**
MCP setup is broken for most developers. The `spawn npx ENOENT` error alone has thousands stuck. GitHub MCP's org-level PAT restrictions block most teams. No existing tool (Smithery, MCPM, mcp-installer) solves the prerequisite setup — they only handle package installation.

We built setup scripts that solve these specific pain points. They run locally, cost us nothing, and every search for "github mcp setup" or "spawn npx ENOENT fix" can land on our site.

**Decision:**
Ship OS-specific setup scripts (`.sh` for macOS/Linux, `.ps1` for Windows) as free, open-source tools under the Context Bharat brand. Host the guide pages on contextbharat.com for SEO. Keep scripts in the public GitHub repo.

Planned tools (in priority order):
1. GitHub MCP Setup (shipped)
2. Context Bharat MCP Setup (shipped)
3. MCP Doctor (diagnoses ENOENT, JSON errors, token issues)
4. Multi-Tool Config Sync (sync MCP configs across Claude/Cursor/VS Code/Windsurf)
5. Jira/Confluence MCP Setup (huge Indian IT services audience)
6. Supabase MCP Setup (popular with Indian indie hackers)
7. "First MCP in 5 Minutes" onboarding (targets vibe coders)

**Consequences:**
- Zero infra cost — scripts run on user's machine
- SEO traffic for "github mcp setup", "spawn npx enoent", "mcp not working"
- Brand awareness before user needs our core product
- Every setup script has a soft CTA for Context Bharat MCP
- Scripts are Apache 2.0 — anyone can fork, but they carry our brand
- Must maintain scripts as MCP ecosystem evolves

---

## Future Decisions (Pending)

- **ADR-013:** Qdrant migration trigger criteria and migration strategy
- **ADR-014:** Self-hosting offering for enterprise customers
- **ADR-015:** Southeast Asia expansion (GrabPay, GoPay, GCash APIs)
- **ADR-016:** MCP Marketplace listing strategy
