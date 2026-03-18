# Roadmap

What we're building, what's done, and what's next. Updated weekly.

---

## Current Sprint (Week 1–2): Foundation

**Goal:** MCP server running locally, backend API live, first 8 libraries indexed.

- [ ] Fork upstash/context7 MCP client → rename to @contextbharat/mcp
- [ ] Update MCP client to point to our backend API URL
- [ ] FastAPI backend skeleton with `/v1/libraries/resolve` and `/v1/docs/query`
- [ ] Supabase schema: libraries + doc_chunks + api_keys tables
- [ ] pgvector extension enabled + index created
- [ ] Crawl4AI web crawler working for docs sites
- [ ] OpenAI embedding integration
- [ ] Ingest Razorpay (first library — best docs, validates pipeline)
- [ ] Ingest Cashfree, Setu, Next.js, FastAPI, React, Supabase, Prisma
- [ ] Basic MCP inspector test: resolve + query working end-to-end
- [ ] `.env.example` with all required variables
- [ ] `docker-compose.yml` for local dev (Postgres + Redis)
- [ ] `Makefile` with common commands

---

## Sprint 2 (Week 3–4): PDF & Govt APIs

**Goal:** PDF/OCR pipeline working, ONDC and UPI specs indexed.

- [ ] pdfplumber integration for text-based PDFs
- [ ] Tesseract OCR integration for scanned PDFs
- [ ] PDF table extraction → Markdown conversion
- [ ] Ingest ONDC Protocol Specs (132 repos + PDFs)
- [ ] Ingest UPI/NPCI specs (PDF-only)
- [ ] Ingest GSTN API docs
- [ ] Ingest DigiLocker API spec
- [ ] Ingest Bhashini API
- [ ] OCR confidence scoring + low-confidence flagging
- [ ] Celery task queue for async ingestion
- [ ] GitHub Actions daily cron for re-indexing

---

## Sprint 3 (Week 5–6): Trading + Enterprise + Hindi

**Goal:** 30+ libraries indexed, Hindi docs for top 5 libraries.

- [ ] Zerodha Kite API indexed
- [ ] Upstox API v3 indexed
- [ ] AngelOne SmartAPI indexed
- [ ] Zoho CRM + Zoho Books API indexed
- [ ] Frappe/ERPNext indexed (GitHub)
- [ ] Sarvam AI translation integration
- [ ] Hindi docs generated for: Razorpay, ONDC, GSTN, Zerodha Kite, Bhashini
- [ ] REST API v1 complete with rate limiting
- [ ] Redis response caching
- [ ] Cohere reranking integration
- [ ] `/v1/libraries` endpoint (list all libraries)

---

## Sprint 4 (Week 7–8): Frontend + Auth

**Goal:** Working web dashboard with API key management.

- [ ] Next.js 15 project setup with Supabase Auth
- [ ] Landing page (use content from `website/content.md`)
- [ ] Google OAuth login
- [ ] API key generation + display
- [ ] Usage dashboard (queries today, this month)
- [ ] Library browser (search + filter by category)
- [ ] Interactive query sandbox (test any library + query in browser)
- [ ] MCP setup guide page (copy-paste instructions for Claude/Cursor)
- [ ] Offline documentation pack download (top 30 libraries)

---

## Sprint 5 (Week 9–10): Launch

**Goal:** Public launch, open-source release, community GTM.

- [ ] Performance optimization (p99 latency < 2s for query-docs)
- [ ] Error monitoring (Sentry)
- [ ] Ingestion failure alerts (Slack webhook)
- [ ] Apache 2.0 LICENSE file
- [ ] README.md with 1-minute quickstart
- [ ] Publish @contextbharat/mcp to npm
- [ ] Deploy to production (Railway + Vercel)
- [ ] Cloudflare Worker for edge caching
- [ ] Product Hunt submission prepared
- [ ] FOSS United event demo prepared
- [ ] 100 libraries indexed at launch
- [ ] MeitY TIDE 2.0 grant application submitted

---

## Backlog (Post-Launch)

### Month 4–6
- [ ] Stripe integration for Pro billing (₹399/mo)
- [ ] Team plan (₹999/seat)
- [ ] Private library indexing (connect your own GitHub repo)
- [ ] VS Code extension
- [ ] Qdrant migration (when pgvector hits limits)
- [ ] Account Aggregator (Sahamati) indexed
- [ ] ABDM Health APIs indexed
- [ ] PhonePe Business API indexed

### Month 6–12
- [ ] Self-hosted deployment option (enterprise)
- [ ] Tamil documentation for top 10 libraries
- [ ] ONDC seller app starter template (ONDC + AI)
- [ ] Southeast Asia expansion: GrabPay, GoPay, GCash APIs
- [ ] MCP Marketplace listing
- [ ] "Document-a-thon" event infrastructure (submission portal, scoring)
- [ ] Sponsored library program (API provider pays for featured placement)
- [ ] API for agent pipelines (higher rate limits, streaming responses)

---

## Metrics We Track

| Metric | Current | Month 3 Goal | Month 12 Goal |
|--------|---------|-------------|---------------|
| Libraries indexed | 0 | 100 | 300+ |
| Registered users | 0 | 500 | 10,000 |
| Pro subscribers | 0 | 50 | 2,000 |
| MRR | ₹0 | ₹20K | ₹80L |
| Daily queries | 0 | 5,000 | 200,000 |
| p99 query latency | — | <2s | <1s |
| Indian API coverage | 0% | 60% | 90% |
