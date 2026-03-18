# Infrastructure

Complete infra setup, costs, and scaling strategy.

---

## Services Overview

| Service | Provider | Purpose | Monthly Cost (MVP) |
|---------|----------|---------|-------------------|
| Backend API | Railway | FastAPI Python app | $20 |
| Celery Workers | Railway | Async ingestion jobs | $15 |
| Vector DB + Auth | Supabase | pgvector + Postgres + Auth | $25 |
| Redis (cache + queue) | Upstash | Response cache + Celery broker | $10 |
| Frontend | Vercel | Next.js hosting | $0 (free) |
| CDN + Edge | Cloudflare | DNS + Workers + caching | $5 |
| Embeddings | OpenAI | text-embedding-3-small | $20–40 |
| Reranking | Cohere | Rerank v3 API | $15–20 |
| Translation | Sarvam AI | Hindi + regional | $0 (startup credits) |
| **Total** | | | **~$110–135/mo** |

---

## Railway Setup (Backend + Workers)

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login

# Create project
railway init context7india

# Deploy backend service
railway up --service backend

# Add environment variables
railway variables set SUPABASE_URL=... OPENAI_API_KEY=... COHERE_API_KEY=...

# Add Celery worker service
railway service create --name celery-worker
railway up --service celery-worker

# Check logs
railway logs --service backend
railway logs --service celery-worker
```

**railway.json** (in `/backend/`):
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
```

**railway.json for Celery worker:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2"
  }
}
```

---

## Supabase Setup

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Run migrations (via Alembic)
-- alembic upgrade head

-- Enable Row Level Security on api_keys
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own keys" ON api_keys
  FOR ALL USING (auth.uid() = user_id);

-- RLS on usage tracking (if added)
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
```

**Supabase free tier limits:**
- 500MB database (sufficient for ~5M doc chunks at MVP)
- 1GB file storage
- 50K monthly active users
- 2 CPU, 1GB RAM shared

**Upgrade trigger:** When database exceeds 400MB or we hit CPU limits on query load.
**Pro plan:** $25/month → 8GB DB, dedicated compute.

---

## Upstash Redis Setup

```bash
# Install Upstash CLI or use dashboard
# Create Redis database (Singapore region for India latency)

# Environment variables
UPSTASH_REDIS_URL=redis://...
UPSTASH_REDIS_TOKEN=...

# Usage in backend
from upstash_redis import Redis
redis = Redis.from_env()

# Cache API responses
await redis.setex(cache_key, 300, json.dumps(response))  # 5-min TTL
result = await redis.get(cache_key)
```

**Free tier:** 10K commands/day. **Pay as you go:** $0.2 per 100K commands.

---

## Cloudflare Setup

**DNS:** All domains managed in Cloudflare DNS.

**Workers** — edge caching for MCP responses:
```javascript
// cloudflare-worker/index.js
export default {
  async fetch(request, env) {
    const cacheKey = new Request(request.url, request);
    const cache = caches.default;

    // Check cache
    let response = await cache.match(cacheKey);
    if (response) return response;

    // Fetch from origin (Railway)
    response = await fetch(`https://api-origin.context7india.com${new URL(request.url).pathname}`, request);

    // Cache GET requests for 5 minutes
    if (request.method === "GET" && response.ok) {
      const cacheResponse = new Response(response.body, response);
      cacheResponse.headers.set("Cache-Control", "max-age=300");
      await cache.put(cacheKey, cacheResponse.clone());
    }

    return response;
  }
};
```

---

## GitHub Actions

### Daily Ingestion Cron

```yaml
# .github/workflows/daily-ingest.yml
name: Daily Documentation Re-index

on:
  schedule:
    - cron: "30 20 * * *"  # 2 AM IST (8:30 PM UTC)
  workflow_dispatch:         # Manual trigger

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements.txt
      - name: Trigger ingestion
        env:
          CONTEXT7INDIA_API_KEY: ${{ secrets.INTERNAL_API_KEY }}
          CONTEXT7INDIA_API_BASE_URL: ${{ secrets.API_BASE_URL }}
        run: |
          python backend/scripts/trigger_scheduled_ingestion.py
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
      redis:
        image: redis:7
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest tests/unit tests/integration -v --cov=app
        env:
          DATABASE_URL: postgresql://postgres:test@localhost/test_db
          REDIS_URL: redis://localhost:6379

  test-mcp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd mcp-server && pnpm install && pnpm test

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd frontend && pnpm install && pnpm build && pnpm test
```

---

## Cost Scaling Model

| Phase | Users | DB size | Infra/mo | LLM/mo | Total/mo |
|-------|-------|---------|----------|--------|----------|
| MVP | 0–100 | 200MB | $55 | $80 | **$135** |
| Launch | 1K active | 1GB | $200 | $300 | **$500** |
| Growth | 10K active | 5GB | $800 | $1,200 | **$2,000** |
| Scale | 100K active | 50GB (Qdrant) | $4,000 | $8,000 | **$12,000** |

At 100K users × ₹399 Pro = ₹4Cr MRR (~$480K/mo). Infra is 2.5% of revenue.

---

## Environment Variables Reference

See `.env.example` for all variables. Critical secrets:

```bash
# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...           # Service role key (server-only)
SUPABASE_ANON_KEY=eyJ...              # Anon key (frontend)
DATABASE_URL=postgresql://...         # Direct Postgres URL for migrations

# AI APIs
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...
SARVAM_API_KEY=...

# Cache
UPSTASH_REDIS_URL=redis://...
UPSTASH_REDIS_TOKEN=...

# Internal
INTERNAL_API_KEY=...                   # For GitHub Actions → API calls
GITHUB_TOKEN=...                       # For GitHub API crawling (higher rate limit)

# MCP Server
CONTEXT7INDIA_API_BASE_URL=https://api.context7india.com
CONTEXT7INDIA_API_KEY=...              # Used by remote MCP server

# Monitoring (optional)
SLACK_WEBHOOK_URL=...                  # For ingestion failure alerts
SENTRY_DSN=...                         # Error tracking
```
