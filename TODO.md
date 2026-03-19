# Context Bharat — Master TODO

> **Goal:** Popularity first (like Context7), profitability second (target 30% PAT).
> Spread adoption aggressively. Make it free/cheap enough that every Indian dev uses it.

---

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done

---

## 1. FOUNDATION (Current — Week 1-2)

### Core Backend
- [ ] Fork upstash/context7 MCP client → rename to `@contextbharat/mcp`
- [ ] FastAPI backend skeleton (`/v1/libraries/resolve`, `/v1/docs/query`)
- [ ] Supabase schema: `libraries`, `doc_chunks`, `api_keys` tables
- [ ] pgvector extension + IVFFlat index
- [ ] Crawl4AI web crawler integration
- [ ] OpenAI embedding integration (text-embedding-3-small)
- [ ] Docker-compose for local dev (Postgres + Redis)
- [ ] Makefile with common commands
- [ ] `.env.example` with all required variables

### First Libraries
- [ ] Ingest Razorpay (validates full pipeline)
- [ ] Ingest Cashfree, Setu
- [ ] Ingest Next.js, FastAPI, React, Supabase, Prisma
- [ ] MCP Inspector end-to-end test: resolve + query working

---

## 2. DEPLOYMENT (Next — see `docs/deployment-plan.md`)

### Infrastructure Setup
- [ ] Register `contextbharat.com` domain on Cloudflare
- [ ] Create Supabase project (Mumbai region)
- [ ] Create Upstash Redis (Mumbai region)
- [ ] Create Railway project, connect GitHub repo
- [ ] Create Vercel project, connect GitHub repo
- [ ] Set up Cloudflare Workers project (`wrangler init`)

### Deploy
- [ ] Adapt MCP server to Cloudflare Workers runtime (HTTP Streamable)
- [ ] Deploy MCP server: `wrangler deploy`
- [ ] Point `mcp.contextbharat.com` to Workers custom domain
- [ ] Deploy backend to Railway (auto from GitHub push)
- [ ] Run Alembic migrations on Supabase
- [ ] Deploy frontend to Vercel
- [ ] Configure all env vars across services
- [ ] Test MCP connection from Claude Desktop end-to-end

### Cost target: ~$5/mo MVP

---

## 3. USAGE TRACKER (Next priority)

> Both admin-level and user-level. Critical for credit billing and growth tracking.

### User-Facing Dashboard
- [ ] Real-time credit balance display
- [ ] Query history (last 50 queries with timestamp, library, credits used)
- [ ] Daily/weekly/monthly usage chart (Recharts)
- [ ] Credits remaining alert (20%, 10%, 0% thresholds)
- [ ] Per-library usage breakdown (which APIs user queries most)
- [ ] Export usage data as CSV

### Admin Dashboard
- [ ] Total queries today / this week / this month (global)
- [ ] Active users (DAU / WAU / MAU)
- [ ] Top 10 most queried libraries
- [ ] Top 10 users by query volume
- [ ] Revenue dashboard: credits purchased, credits consumed, revenue by pack
- [ ] Cost dashboard: OpenAI embedding cost, Cohere rerank cost, infra cost
- [ ] Margin tracker: revenue - costs = margin (target 30% PAT)
- [ ] Library health: freshness scores, ingestion failures, stale docs
- [ ] Signup funnel: visitors → signups → first query → credit purchase
- [ ] Geographic distribution of users (city-level if possible)

### Backend: Usage Metering
- [ ] `usage_events` table (append-only, every API call logged)
  ```sql
  CREATE TABLE usage_events (
      id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id     UUID REFERENCES auth.users(id),
      event_type  TEXT NOT NULL,        -- 'query', 'resolve', 'translate'
      library_id  TEXT,
      credits_used INTEGER DEFAULT 1,
      latency_ms  INTEGER,
      cache_hit   BOOLEAN DEFAULT FALSE,
      ip_address  INET,
      user_agent  TEXT,
      created_at  TIMESTAMPTZ DEFAULT NOW()
  );
  ```
- [ ] Middleware to log every API call to `usage_events`
- [ ] Aggregation views for admin dashboard (materialized views for performance)
- [ ] Daily rollup job (aggregate raw events → daily summaries)
- [ ] API endpoints: `GET /v1/usage/me` (user), `GET /v1/admin/usage` (admin)

### Frontend: Dashboard Pages
- [ ] `/dashboard` — user usage overview + credit balance
- [ ] `/dashboard/usage` — detailed usage history + charts
- [ ] `/admin` — admin-only dashboard (protected by role)
- [ ] `/admin/usage` — global usage analytics
- [ ] `/admin/revenue` — revenue + margin tracking

---

## 4. CREDIT BILLING SYSTEM (see `docs/pricing-strategy.md`)

### Database
- [ ] `credit_wallets` table (user_id, balance, total_purchased)
- [ ] `credit_ledger` table (append-only, idempotency keys)
- [ ] Atomic credit deduction on every query (optimistic locking)

### Free Tier
- [ ] 50 credits/day without account (IP-based rate limit)
- [ ] 200 credits/day with free account
- [ ] Daily credit reset job (or rolling window)

### Payment Integration
- [ ] Razorpay integration for credit packs (₹99 / ₹399 / ₹999 / ₹3,999)
- [ ] Razorpay webhook → add credits atomically
- [ ] Purchase flow in frontend (select pack → Razorpay checkout → credits added)
- [ ] Purchase history page
- [ ] Stripe integration for international users (later)

### Credit Policies
- [ ] Credits never expire
- [ ] No auto-reload by default
- [ ] Optional auto-reload setting (user can enable)
- [ ] Email alerts at 20%, 10%, 0% balance

---

## 5. PDF & GOVT APIs (Sprint 2)

- [ ] pdfplumber integration for text-based PDFs
- [ ] Tesseract OCR for scanned PDFs
- [ ] PDF table extraction → Markdown
- [ ] Ingest ONDC Protocol Specs (132 repos + PDFs)
- [ ] Ingest UPI/NPCI specs (PDF-only)
- [ ] Ingest GSTN API docs
- [ ] Ingest DigiLocker API spec
- [ ] OCR confidence scoring + low-confidence flagging
- [ ] Celery task queue for async ingestion
- [ ] GitHub Actions daily cron for re-indexing

---

## 6. TRADING + ENTERPRISE + HINDI (Sprint 3)

- [ ] Zerodha Kite API indexed
- [ ] Upstox API v3 indexed
- [ ] AngelOne SmartAPI indexed
- [ ] Zoho CRM + Books indexed
- [ ] Frappe/ERPNext indexed
- [ ] Sarvam AI translation integration
- [ ] Hindi docs for: Razorpay, ONDC, GSTN, Zerodha, Bhashini
- [ ] Cohere reranking integration
- [ ] Redis response caching

---

## 7. FRONTEND + AUTH (Sprint 4)

- [ ] Next.js 15 project setup with Supabase Auth
- [ ] Landing page (from `website/content.md`)
- [ ] Google OAuth login
- [ ] API key generation + display
- [ ] Usage dashboard (integrates with #3 above)
- [ ] Library browser (search + filter by category)
- [ ] Interactive query sandbox
- [ ] MCP setup guide page
- [ ] Credit purchase flow (integrates with #4 above)

---

## 8. LAUNCH (Sprint 5)

- [ ] Performance optimization (p99 < 2s)
- [ ] Sentry error monitoring (free tier)
- [ ] Ingestion failure Slack alerts
- [ ] Apache 2.0 LICENSE
- [ ] README.md with 1-minute quickstart
- [ ] Publish `@contextbharat/mcp` to npm
- [ ] Cloudflare Worker edge caching live
- [ ] 100 libraries indexed

---

## 8.5. REPO SPLIT — Open Source vs Private

> Split codebase into public GitHub (community, SEO) + private Bitbucket (moat, deploys)

### Public GitHub Repo
- [x] `mcp-server/` — Apache 2.0 MCP client
- [x] `tools/` — Free setup scripts (GitHub MCP .sh + .ps1, Context Bharat, All)
- [x] `frontend/app/setup/` — Setup tool pages with OS detection
- [x] `frontend/app/(public)/` — Landing, docs, pricing pages
- [ ] `backend/config/libraries/` — Library JSON configs
- [x] `docs/` — Philosophy, decisions, contributing, style guide
- [x] `knowledge-base/api-catalog.md` — Library catalog
- [x] `website/` — Marketing copy
- [ ] `.github/` — Issue templates, PR templates (community-facing)
- [ ] Strip private code before first public push

### Private Bitbucket Repo
- [ ] Create `bitbucket.org/contextbharat/context-bharat-private`
- [ ] Full backend (ingestion, services, repositories, tasks, migrations)
- [ ] Dashboard + admin frontend pages
- [ ] CI/CD pipelines (deploy from Bitbucket)
- [ ] `.env` files and secrets
- [ ] Set up Bitbucket Pipelines for Railway + Vercel deploy

### Sync Process
- [ ] Document manual sync process (GitHub library configs → Bitbucket)
- [ ] Webhook or GitHub Action to notify on new library config PRs

---

## 8.6. FREE SETUP TOOLS — Growth Engine

> Zero-cost traffic drivers. Every "mcp not working" search lands on us.

### Shipped
- [x] `tools/setup-github-mcp.sh` — macOS/Linux GitHub MCP setup
- [x] `tools/setup-github-mcp.ps1` — Windows PowerShell GitHub MCP setup
- [x] `tools/setup-contextbharat-mcp.sh` — Context Bharat MCP setup
- [x] `tools/setup-all-mcp.sh` — Combined setup
- [x] `/setup` page — Tools hub (frontend)
- [x] `/setup/github-mcp` page — OS-auto-detect detail page
- [x] Website content updated with tools section
- [x] Homepage banner + nav link to tools

### Next Tools (prioritized)
- [ ] MCP Doctor script — diagnose ENOENT, JSON errors, stale tokens
- [ ] Multi-tool config sync — edit once, sync to Claude/Cursor/VS Code/Windsurf
- [ ] Jira/Confluence MCP setup — Base64 encoding guide, huge Indian IT audience
- [ ] Supabase MCP setup — region gotcha, read-only mode
- [ ] "First MCP in 5 Minutes" — beginner onboarding, installs node if needed
- [ ] Windows .ps1 versions for all scripts

### Distribution
- [ ] Host scripts at `contextbharat.com/setup/*.sh` and `*.ps1` for curl/irm
- [ ] Blog: "How to fix GitHub MCP org access denied" (SEO)
- [ ] Blog: "spawn npx ENOENT — the fix for every MCP server" (SEO)
- [ ] Reddit post on r/ClaudeAI and r/developersIndia

---

## 9. GROWTH & POPULARITY (Post-Launch)

> Priority: Spread adoption. Every Indian dev should know about this.

### Distribution Channels
- [ ] Product Hunt launch
- [ ] FOSS United event demo
- [ ] r/india, r/developersIndia Reddit posts
- [ ] Twitter/X launch thread (@contextbharat)
- [ ] Dev.to + Hashnode articles ("How to use Razorpay with Claude")
- [ ] YouTube tutorial: "Build ONDC app with AI + Context Bharat"
- [ ] Hacker News Show HN post
- [ ] Claude Desktop Extensions marketplace listing (`.mcpb`)
- [ ] MCP Marketplace listing

### Community & Virality
- [ ] Document-a-thon events (community adds libraries for prizes)
- [ ] "Powered by Context Bharat" badge for open-source projects
- [ ] Referral credits: invite a friend → both get 500 free credits
- [ ] GitHub star milestone celebrations (share on Twitter)
- [ ] Student program: Pro-equivalent free for verified students
- [ ] College ambassador program (top CS colleges in India)

### Partnerships
- [ ] iSPIRT community integration (India Stack APIs)
- [ ] Approach Razorpay, Zerodha for "sponsored library" deals
- [ ] FOSS United partnership for events
- [ ] MeitY TIDE 2.0 grant application

### Content Marketing
- [ ] Blog: "Why Indian API docs are broken" (SEO bait)
- [ ] Blog: "Context7 vs Context Bharat" (comparison)
- [ ] Blog: "Building with ONDC is hard. We made it easy."
- [ ] Weekly Twitter thread: "Indian API of the week"

---

## 10. PROFITABILITY TRACKING

> Target: 30% PAT (Profit After Tax)

### Revenue Levers
- Credit pack sales (primary)
- Sponsored libraries (₹50K-2L/year per API provider)
- Team/enterprise deals (custom credit volumes)

### Cost Structure (per month at scale)
| Cost | MVP | 10K users |
|------|-----|-----------|
| Infra (Railway + services) | $5 | $70 |
| OpenAI embeddings | $20 | $100 |
| Cohere reranking | $15 | $80 |
| Domain + misc | $1 | $5 |
| **Total** | **$41** | **$255** |

### Break-Even Target
At ₹0.011/query cost and ₹0.016/query revenue (Builder pack):
- Margin per query: ₹0.005 (31%)
- Break-even at ~$41/mo cost: ~₹3,400/mo revenue = ~85 Builder packs
- That's ~85 paying users out of potentially thousands of free users

### Monthly P&L Template
```
Revenue
  Credit pack sales:     ₹_____
  Sponsored libraries:   ₹_____
  Total Revenue:         ₹_____

Costs
  Infrastructure:        ₹_____
  AI APIs (OpenAI+Cohere): ₹_____
  Payment gateway fees:  ₹_____ (2% Razorpay)
  Total Costs:           ₹_____

Gross Profit:            ₹_____
Tax (30%):               ₹_____
Net Profit (PAT):        ₹_____
PAT Margin:              ___%  (target: 30%)
```

---

## Priority Order

1. **Foundation** — get the core working
2. **Deployment** — get it live at mcp.contextbharat.com
3. **Usage Tracker** — know who's using what (critical for everything else)
4. **Credit Billing** — start monetizing
5. **More Libraries** — PDF/govt/trading APIs expand the moat
6. **Frontend** — dashboard, auth, purchase flow
7. **Launch** — go public
8. **Growth** — spread like wildfire
9. **Profitability** — hit 30% PAT target
