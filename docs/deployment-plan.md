# contextBharat — Deployment Plan & Infrastructure

## TL;DR Recommendation (Updated March 2026)

**Revised approach: Cloudflare Workers (MCP) + Railway (Backend) + Free tiers everywhere**
- MVP cost: **~$5/mo** (Railway Hobby only, everything else free)
- Launch cost: **~$30/mo**
- 10K users: **~$70/mo**
- One-click deploy, no manual infra management
- Follows industry patterns: GitHub MCP (stdio + HTTP Streamable), Zerodha Kite MCP (hosted at mcp.kite.trade)

### Why the change from GCP Cloud Run
- GCP requires more setup complexity (IAM, project config, billing alerts)
- Railway + Cloudflare Workers = same result with 80% less setup
- Traffic will be very low for months — free tiers are sufficient
- One-click deploy via GitHub integration, not IaC overhead

---

## Industry Reference: How Others Deploy MCP Servers

| Server | Transport | Hosting | User Setup |
|--------|-----------|---------|------------|
| **GitHub MCP** | STDIO (local) + HTTP Streamable (remote) | Local subprocess OR Anthropic Desktop Extensions (`.mcpb` one-click install) | One-click / add URL |
| **Zerodha Kite MCP** | HTTP `/mcp` + `/sse` endpoints | Hosted at `mcp.kite.trade` — zero install needed. Also self-hostable (Go binary) | Add URL to Claude config |

Both offer **zero-config for end users** — that's the 2026 standard.

**Key takeaways:**
- HTTP Streamable is the current production standard (SSE deprecated since MCP spec 2025-03-26)
- Hosted remote servers = best UX (users just add a URL)
- Also offer local/STDIO for offline/power users

---

## Revised Deployment Stack (Free/Cheap for MVP)

| Component | Deploy To | Cost | Why |
|-----------|-----------|------|-----|
| **MCP Server** (TypeScript) | **Cloudflare Workers** | **$0** (100K req/day free) | Zero cold starts, global edge, `wrangler deploy` |
| **Backend API** (FastAPI) | **Railway** (Hobby) | **$5/mo** | Docker-based, auto-deploy from GitHub push |
| **Celery Workers** | **Railway** (same project) | Included in $5 | Separate service in same Railway project |
| **Database + Auth** | **Supabase** (Free tier) | **$0** (500MB, 50K MAUs) | pgvector included, auth included |
| **Redis/Cache** | **Upstash** (Free tier) | **$0** (10K commands/day) | Serverless, no idle cost |
| **Frontend** | **Vercel** (Hobby) | **$0** | Next.js native, CDN, auto-deploy |
| **DNS + CDN** | **Cloudflare** (Free) | **$0** | DNS, SSL, edge caching |

### Total MVP: ~$5/month (vs original plan ~$110-135/mo = 95% cheaper)

---

## One-Click Setup for Users

### Remote (recommended — zero install)
```json
{
  "mcpServers": {
    "context-bharat": {
      "type": "http",
      "url": "https://mcp.contextbharat.com/mcp"
    }
  }
}
```

### Local (offline/power users)
```bash
npx @contextbharat/mcp --api-key YOUR_API_KEY
```

### Future: Desktop Extension
Publish a `.mcpb` bundle for literal one-click install from Claude Desktop marketplace.

---

## One-Click Deploy for Us

### MCP Server → Cloudflare Workers
```bash
npm install -g wrangler
wrangler login
wrangler deploy   # Live at mcp.contextbharat.com/mcp
```
- Custom domain `mcp.contextbharat.com` → free on Workers
- Adapt `mcp-server/src/index.ts` to Workers runtime (HTTP Streamable)

### Backend → Railway
- Connect GitHub repo → auto-deploys on push to `main`
- Set env vars in Railway dashboard
- No Dockerfile changes needed (Railway uses Nixpacks or existing Dockerfile)

### Frontend → Vercel
- Connect GitHub repo → auto-deploys on push
- Zero config for Next.js

### Database → Supabase
- Create project in dashboard (Mumbai region)
- Run Alembic migrations
- Done.

---

## Scaling Migration Path

| Phase | Traffic | What Changes | Cost |
|-------|---------|-------------|------|
| **Now (MVP)** | <100 users | Free tiers + Railway Hobby | **~$5/mo** |
| **Traction** | 1K users | Upgrade Supabase to Pro ($25/mo) | **~$30/mo** |
| **Growth** | 10K users | Railway Pro ($20/mo) + more workers | **~$70/mo** |
| **Scale** | 100K users | Move backend to AWS ECS/Lambda + Qdrant | **~$200+/mo** |

---

## Implementation Checklist

### Phase 1: Setup (Day 1-2)
- [ ] Register `contextbharat.com` domain on Cloudflare
- [ ] Create Supabase project (Mumbai region), enable pgvector
- [ ] Create Upstash Redis (Mumbai region)
- [ ] Create Railway project, connect GitHub repo
- [ ] Create Vercel project, connect GitHub repo
- [ ] Set up Cloudflare Workers project with `wrangler init`

### Phase 2: Deploy (Day 3-4)
- [ ] Adapt MCP server to Cloudflare Workers runtime (HTTP Streamable)
- [ ] Deploy MCP server: `wrangler deploy`
- [ ] Point `mcp.contextbharat.com` to Workers (custom domain)
- [ ] Deploy backend to Railway (auto from GitHub push)
- [ ] Run Alembic migrations on Supabase
- [ ] Deploy frontend to Vercel
- [ ] Configure all env vars across services

### Phase 3: Validate (Day 5)
- [ ] Test MCP connection from Claude Desktop
- [ ] Test all API endpoints via MCP Inspector
- [ ] Run ingestion for first libraries
- [ ] Set up Sentry (free tier) for error tracking
- [ ] Set up Slack webhook for ingestion failure alerts

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MCP transport | HTTP Streamable | Industry standard (2026), SSE deprecated |
| MCP hosting | Cloudflare Workers | Free, zero cold starts, global edge |
| Backend hosting | Railway | Simplest Docker hosting, $5/mo |
| No IaC (Pulumi) for MVP | Manual dashboard setup | Premature for <100 users, adds complexity |
| No Kubernetes | Railway services | Overkill until 10K+ users |

---

## Cost Comparison: Before vs After

| | Old Plan (GCP Cloud Run) | New Plan (CF Workers + Railway) |
|---|---|---|
| MVP (Month 0-3) | $0-20/mo | **$5/mo** |
| Launch (Month 3-6) | $45-75/mo | **$30/mo** |
| Growth (10K users) | $150-400/mo | **$70/mo** |
| Setup complexity | High (GCP IAM, Pulumi) | **Low (dashboard + wrangler)** |
| Deploy method | `pulumi up` | **GitHub push (auto-deploy)** |

---

## Original Analysis (Kept for Reference)

## Cloud Platform Comparison

### Compute

| Platform | MVP (0-1K users) | Growth (10K) | Free Tier | India Region | Ease | Docker | IaC |
|----------|-----------------|-------------|-----------|-------------|------|--------|-----|
| **GCP Cloud Run** | $0-10/mo | $150-500/mo | 180K vCPU-sec, 2M req/mo | Mumbai | 3/5 | Yes | Terraform, Pulumi |
| **AWS Fargate** | $50-120/mo | $300-800/mo | 12 months limited | Mumbai | 2/5 | Yes | Terraform, CDK, SST |
| **Railway** | $5-25/mo | $80-250/mo | $5 trial credit | Singapore | 5/5 | Yes | No native IaC |
| **Fly.io** | $5-25/mo | $80-300/mo | Small free allowance | Mumbai | 4/5 | Yes | Terraform |
| **Render** | $7-30/mo | $100-350/mo | 750 hrs free | Singapore | 4/5 | Yes | Blueprints YAML |
| **Azure Container Apps** | $20-70/mo | $200-600/mo | 180K vCPU-sec free | Central India | 2/5 | Yes | Terraform, Bicep |
| **DigitalOcean** | $5-30/mo | $100-400/mo | Free static sites | Bangalore | 4/5 | Yes | Terraform |
| **Hetzner** | $4-15/mo | $40-150/mo | None | Singapore | 3/5 | Yes (VPS) | Terraform |

### Database (PostgreSQL + pgvector)

| Platform | MVP | Growth | Free Tier | India | pgvector |
|----------|-----|--------|-----------|-------|----------|
| **Supabase** | $0/mo | $25-100/mo | 500MB DB, 50K MAUs | Mumbai + Pune | Yes |
| **Neon** | $0/mo | $30-100/mo | 0.5GB, scale-to-zero | Singapore | Yes |
| **AWS RDS** | $0-30/mo | $100-300/mo | 12 months t3.micro | Mumbai | Yes |
| **GCP Cloud SQL** | $10-40/mo | $100-300/mo | $300 trial (90 days) | Mumbai | Yes |

### Redis / Cache

| Platform | MVP | Growth | Free Tier | India |
|----------|-----|--------|-----------|-------|
| **Upstash** | $0/mo | $5-20/mo | 500K commands/mo | Mumbai |
| **AWS ElastiCache** | $15-30/mo | $50-200/mo | None | Mumbai |

### Frontend / CDN

| Platform | MVP | Growth | Free Tier |
|----------|-----|--------|-----------|
| **Vercel** | $0/mo | $20/mo (Pro) | 100GB bandwidth, unlimited deploys |
| **Cloudflare Pages** | $0/mo | $0-5/mo | Unlimited sites, 500 builds/mo |

---

## Startup Credit Programs

| Provider | Credits | Eligibility | Duration |
|----------|---------|-------------|----------|
| **GCP (Google for Startups)** | Up to $200K ($350K for AI) | Funded startups | 2 years |
| **Azure (Founders Hub)** | Up to $150K | No VC required for $5K tier | Tiered |
| **AWS (Activate)** | Up to $100K | Pre-Series B | 12-24 months |
| **DigitalOcean (Hatch)** | Up to $100K | Apply online | Program-based |

**Action**: Apply for GCP and AWS credits immediately. Both can be done in parallel.

---

## Recommended Architecture (Option C)

```
Developer's AI Tool (Claude / Cursor / VS Code)
        |
        | MCP Protocol
        v
[ MCP Server — GCP Cloud Run (Mumbai) ]
        |
        | REST API
        v
[ FastAPI Backend — GCP Cloud Run (Mumbai) ]
  |              |              |
  v              v              v
[ Supabase ]  [ Upstash ]  [ Celery Worker ]
[ pgvector ]  [ Redis   ]  [ Cloud Run Jobs]
[ Mumbai   ]  [ Mumbai  ]  [ Mumbai        ]
        |
        v
[ Vercel — Next.js Frontend ]
  |
  v
[ Cloudflare CDN — India PoPs ]
```

### Cost Breakdown

#### Phase 1: MVP (Month 0-3) — $0-20/mo

| Service | Provider | Plan | Cost |
|---------|----------|------|------|
| Backend | GCP Cloud Run | Free tier (180K vCPU-sec) | $0 |
| MCP Server | GCP Cloud Run | Free tier | $0 |
| Celery Worker | GCP Cloud Run Jobs | Free tier | $0 |
| Database | Supabase | Free (500MB, pgvector) | $0 |
| Redis | Upstash | Free (500K commands) | $0 |
| Frontend | Vercel | Hobby (free) | $0 |
| CDN | Cloudflare | Free | $0 |
| Domain | Cloudflare | Registration | ~$10/yr |
| **Total** | | | **$0-1/mo** |

#### Phase 2: Launch (Month 3-6) — $45/mo

| Service | Provider | Plan | Cost |
|---------|----------|------|------|
| Backend | GCP Cloud Run | Pay-as-you-go | $5-15/mo |
| MCP Server | GCP Cloud Run | Pay-as-you-go | $3-5/mo |
| Celery Worker | GCP Cloud Run Jobs | Pay-as-you-go | $2-5/mo |
| Database | Supabase | Pro ($25/mo, 8GB DB) | $25/mo |
| Redis | Upstash | Pay-as-you-go | $0-5/mo |
| Frontend | Vercel | Pro ($20/mo) | $20/mo |
| CDN | Cloudflare | Free | $0 |
| **Total** | | | **~$55-75/mo** |

*With GCP startup credits: ~$25-45/mo (GCP services free)*

#### Phase 3: Growth (Month 6-18, 10K users) — $150-400/mo

| Service | Provider | Plan | Cost |
|---------|----------|------|------|
| Backend (2 instances) | GCP Cloud Run | Auto-scale | $50-150/mo |
| MCP Server | GCP Cloud Run | Auto-scale | $20-50/mo |
| Workers (2) | GCP Cloud Run Jobs | As-needed | $20-50/mo |
| Database | Supabase | Pro (dedicated compute) | $50-100/mo |
| Redis | Upstash | Pro | $5-20/mo |
| Frontend | Vercel | Pro | $20-40/mo |
| CDN + R2 | Cloudflare | Free + R2 | $0-5/mo |
| **Total** | | | **$165-415/mo** |

*With GCP credits remaining: ~$95-215/mo*

---

## IaC: Pulumi (TypeScript)

### Why Pulumi over Terraform

| Criteria | Pulumi | Terraform | SST |
|----------|--------|-----------|-----|
| Language | TypeScript, Python, Go | HCL (custom language) | TypeScript |
| Your team knows it? | Yes (TS + Python) | No (HCL is new) | Yes (TS) |
| GCP support | Excellent | Excellent | AWS only |
| Multi-cloud | 60+ providers | 4800+ providers | AWS only |
| State management | Pulumi Cloud (free) or S3 | S3/GCS | AWS |
| Learning curve | Low (use languages you know) | Medium (learn HCL) | Low |

### Pulumi Project Structure

```
infra/
├── Pulumi.yaml          # Project config
├── Pulumi.dev.yaml      # Dev stack config
├── Pulumi.prod.yaml     # Production stack config
├── index.ts             # Main infrastructure definition
├── modules/
│   ├── backend.ts       # Cloud Run for FastAPI + MCP
│   ├── database.ts      # Supabase or Cloud SQL
│   ├── redis.ts         # Upstash Redis
│   ├── frontend.ts      # Vercel deployment
│   ├── cdn.ts           # Cloudflare config
│   └── monitoring.ts    # Alerting, logging
├── package.json
└── tsconfig.json
```

### Deployment Commands

```bash
# Install Pulumi
curl -fsSL https://get.pulumi.com | sh

# Initialize
cd infra && pulumi stack init dev

# Deploy
pulumi up

# Preview changes
pulumi preview

# Destroy (tear down)
pulumi destroy
```

---

## Docker Configuration

### Backend Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# System deps for OCR + PDF
RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-hin poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY config/ ./config/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### MCP Server Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install --production
COPY dist/ ./dist/

CMD ["node", "dist/index.js"]
```

### docker-compose.production.yml

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env.production

  mcp-server:
    build: ./mcp-server
    ports: ["3001:3001"]
    env_file: .env.production

  celery-worker:
    build: ./backend
    command: celery -A app.tasks.celery_app worker --loglevel=info
    env_file: .env.production
```

---

## Deployment Steps

### Week 1: Setup

1. [ ] Register `contextbharat.com` domain (Cloudflare)
2. [ ] Apply for GCP startup credits (Google for Startups)
3. [ ] Apply for AWS Activate credits (parallel)
4. [ ] Create Supabase project (Mumbai region)
5. [ ] Create Upstash Redis (Mumbai region)
6. [ ] Create GCP project + enable Cloud Run
7. [ ] Set up Pulumi project

### Week 2: Deploy

1. [ ] Build Docker images (backend, MCP server)
2. [ ] Push to GCP Artifact Registry
3. [ ] Deploy backend to Cloud Run (Mumbai)
4. [ ] Deploy MCP server to Cloud Run (Mumbai)
5. [ ] Run Alembic migrations on Supabase
6. [ ] Deploy frontend to Vercel
7. [ ] Configure Cloudflare DNS + CDN
8. [ ] Set up environment variables

### Week 3: Validate

1. [ ] Run ingestion for first 15 libraries
2. [ ] Test MCP connection from Claude Desktop
3. [ ] Test all API endpoints
4. [ ] Set up monitoring (GCP Cloud Monitoring)
5. [ ] Set up error alerting (Slack webhook)
6. [ ] Load test with k6

---

## Comparison: Why NOT the Others

| Option | Why Not (for now) |
|--------|-------------------|
| **AWS** | Complex setup, higher cost without credits, overkill for MVP |
| **Railway** | No India region, no pgvector in managed DB |
| **Render** | No India region |
| **Fly.io** | Good but smaller ecosystem, less startup support |
| **Hetzner** | Cheapest but no India region, requires more ops work |
| **Azure** | Complex, weaker Cloud Run equivalent |

**Migrate to AWS when**: Revenue exceeds $5K MRR and you need enterprise features (SOC-2, dedicated VPC, etc.)

---

## Monitoring & Alerting

| What | Tool | Cost |
|------|------|------|
| Error tracking | Sentry (free tier: 5K events/mo) | $0 |
| Uptime monitoring | Better Uptime (free: 10 monitors) | $0 |
| Logs | GCP Cloud Logging (50GB/mo free) | $0 |
| Alerts | Slack webhook + GCP alerting | $0 |
| APM | GCP Cloud Trace (free tier) | $0 |
