# Philosophy

How we build Context Bharat. Read this before writing a single line of code.

---

## 1. India-First, Not India-Only

Our moat is India. No one else can index ONDC's async Beckn Protocol, process GSTN PDF specs through OCR, or provide Zerodha Kite docs in Hindi. That's our unfair advantage.

Global frameworks (React, Next.js, FastAPI, PostgreSQL) are table stakes — we include them because developers need them daily, but they're not our differentiation. When time is limited, always prioritize an Indian API over a global one.

**In practice:**
- Razorpay > Stripe (index Razorpay first, then Stripe)
- ONDC > Shopify (ONDC is uniquely hard, uniquely Indian)
- Krutrim AI > OpenAI (for Indian devs building in India)
- Hindi documentation > another English library

---

## 2. PDF is a First-Class Citizen

Indian government APIs do not live on GitHub. They live in:
- Dense PDF specifications from regulatory bodies
- XML schema files distributed by email
- Documentation behind portal logins requiring organizational registration
- Outdated Word documents on government websites

Our OCR + PDF ingestion pipeline is not an afterthought. It's a core system that must handle:
- Scanned PDFs (image-based, need Tesseract)
- Password-protected PDFs (handle gracefully, log + skip)
- Table extraction from PDF (pdftables, camelot)
- Version detection across PDF revisions
- Chunking PDF content sensibly (respect section boundaries)

If a library's docs are only available as a PDF, we index it. If a developer has to read a PDF to use an API, we've failed them.

---

## 3. AI-Native Development

We build Context Bharat with AI. This is not ironic — it's the point.

- Claude Code writes boilerplate (CRUD endpoints, test skeletons, config parsers)
- Engineers architect, review, and make technical decisions
- Cursor assists with completions inside complex logic
- We **never** use AI for security-critical code without thorough human review
- We **always** write the failing test before asking Claude Code to make it pass

The goal is 3× velocity. 3 engineers shipping what traditionally takes 8.

**AI-native rules:**
- Always give Claude Code context via CLAUDE.md — it reads this file
- Use `/plan` before any complex feature to generate a task spec first
- Keep functions small so AI can reason about them correctly
- Write explicit, descriptive variable names — AI reads them too
- After AI generates code, read every line before committing

---

## 4. Fresh Docs Always

Stale documentation is worse than no documentation. A developer who follows an outdated API example and gets an error loses more time than one who finds no result and checks the official docs.

**Freshness commitments:**
- Every library re-indexed at minimum every 7 days
- High-change libraries (Next.js, Supabase) re-indexed daily
- Version detection: if upstream version bumps, trigger immediate re-index
- Every doc chunk carries a `last_crawled_at` timestamp
- API response includes `freshness_score` so MCP clients can warn on stale data

---

## 5. Offline-First for Tier 2/3

42% of India's new developer jobs are in Tier 2/3 cities. These developers face:
- Inconsistent 4G/5G connectivity
- Bandwidth caps and data costs
- Slow connections that timeout on large API responses

Our offline strategy:
- Pre-downloadable `.contextbharat` packs per library (compressed Markdown + metadata)
- MCP client checks local cache before hitting remote API
- Sync-when-online: detect connectivity, refresh stale local caches
- Pack size targets: <5MB per library, <100MB for top-30 bundle

---

## 6. Hindi and Regional Languages Are Real Features

Not a translation gimmick. Not a future roadmap item. A real feature shipping in Month 3.

43.6% of India speaks Hindi as their mother tongue. Millions of developers learning to code do it in Hindi first. Documentation in Hindi for Razorpay, ONDC, and GSTN doesn't exist anywhere. We build it.

**Approach:**
- Machine translation via Sarvam AI Mayura (purpose-built for Indian languages)
- Human review for terminology accuracy (crowdsourced via community)
- Technical terms kept in English with Hindi explanation
- Code samples always in English — code is universal
- Hindi docs are additive, not replacements for English

Supported languages at launch: Hindi (hi), Tamil (ta), Telugu (te), Kannada (kn), Bengali (bn)

---

## 7. Simple Until It Hurts

We run on Railway + Supabase + Vercel. We don't need Kubernetes. We don't need Elasticsearch. We don't need a data warehouse. We need to ship.

**Default to simpler:**
- pgvector before Qdrant (Qdrant when pgvector can't handle the load)
- Railway before ECS (ECS when Railway can't handle the traffic)
- SQLite in tests before Postgres (Postgres in integration tests)
- Celery before a custom queue (custom queue when Celery becomes the bottleneck)

Add complexity when a specific measured pain demands it. Never speculatively.

---

## 8. Open Community, Closed Index

The MCP client is MIT-licensed and will stay that way. The community should be able to run their own MCP servers pointing to our API.

The ingestion pipeline, vector index, and ranking system are proprietary — this is our business. But we:
- Open-source the library configuration format (`contextbharat.json`)
- Accept community PRs to add new libraries to the index
- Publish detailed API documentation for the REST API
- Provide a self-hostable reference implementation (later, post-revenue)

We do not "open-source wash." If something is closed, we say it plainly.

---

## What We Optimize For (In Order)

1. **Developer time saved** — the only metric that matters
2. **Doc freshness** — stale docs destroy trust
3. **India coverage** — breadth of Indian APIs indexed
4. **Response latency** — MCP tool calls must be fast (<2s p99)
5. **Cost efficiency** — infra cost as % of revenue
6. **Feature breadth** — new capabilities

We do not optimize for GitHub stars (a vanity metric). We optimize for developers saying "I can't build without this."
