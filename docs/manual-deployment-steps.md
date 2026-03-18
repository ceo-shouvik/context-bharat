# Manual Deployment Steps — To Be Automated

These steps were done manually during first deployment. Each section should be
automated via CI/CD (GitHub Actions) or IaC (Pulumi) in the future.

---

## 1. GCP Project Setup (Automate with: Pulumi)

```bash
# Currently manual:
gcloud projects create contextbharat --name="contextBharat"
gcloud billing projects link contextbharat --billing-account=BILLING_ACCOUNT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com orgpolicy.googleapis.com

# Org policy override (needed for public Cloud Run):
gcloud org-policies set-policy policy-reset.yaml --project=contextbharat
# Where policy-reset.yaml contains:
# name: projects/contextbharat/policies/iam.allowedPolicyMemberDomains
# spec:
#   reset: true

# Artifact Registry:
gcloud artifacts repositories create contextbharat --repository-format=docker --location=asia-south1
gcloud auth configure-docker asia-south1-docker.pkg.dev --quiet
```

**To automate**: Pulumi `gcp.projects.Project`, `gcp.projects.Service`, `gcp.artifactregistry.Repository`

---

## 2. Supabase Database Setup (Automate with: Supabase CLI + GitHub Actions)

```bash
# Currently manual via Supabase Dashboard:
# 1. Create project: contextBharat, region: Mumbai, org: Bachao AI
# 2. Run SQL in SQL Editor (see below)
# 3. Copy credentials to Cloud Run env vars

# SQL to run (from backend/alembic/versions/001_initial_schema.py):
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE libraries (...);
CREATE TABLE doc_chunks (...);
CREATE TABLE api_keys (...);
CREATE TABLE ingestion_runs (...);
# + indexes
```

**To automate**:
```bash
# Install Supabase CLI
npm install -g supabase

# Login and link
supabase login
supabase link --project-ref odpnlykpihvdujclaaut

# Run migrations
supabase db push
# OR use Alembic directly:
cd backend && alembic upgrade head
```

**GitHub Actions workflow** (future):
```yaml
- name: Run DB migrations
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: cd backend && alembic upgrade head
```

---

## 3. Docker Build & Push (Automate with: GitHub Actions)

```bash
# Currently manual:
docker build -t asia-south1-docker.pkg.dev/contextbharat/contextbharat/backend:latest backend/
docker push asia-south1-docker.pkg.dev/contextbharat/contextbharat/backend:latest
```

**GitHub Actions workflow** (future):
```yaml
name: Deploy Backend
on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker asia-south1-docker.pkg.dev
      - run: |
          docker build -t asia-south1-docker.pkg.dev/contextbharat/contextbharat/backend:${{ github.sha }} backend/
          docker push asia-south1-docker.pkg.dev/contextbharat/contextbharat/backend:${{ github.sha }}
      - run: |
          gcloud run deploy contextbharat-api \
            --image=asia-south1-docker.pkg.dev/contextbharat/contextbharat/backend:${{ github.sha }} \
            --region=asia-south1 --project=contextbharat
```

---

## 4. Cloud Run Deployment (Automate with: GitHub Actions + Pulumi)

```bash
# Currently manual:
gcloud run deploy contextbharat-api \
  --image=asia-south1-docker.pkg.dev/contextbharat/contextbharat/backend:latest \
  --region=asia-south1 --platform=managed --allow-unauthenticated \
  --port=8000 --memory=512Mi --cpu=1 --min-instances=0 --max-instances=3 \
  --set-env-vars="..." --project=contextbharat

# IAM policy for public access:
gcloud run services add-iam-policy-binding contextbharat-api \
  --region=asia-south1 --member=allUsers --role=roles/run.invoker
```

**To automate**: Pulumi `gcp.cloudrunv2.Service` + `gcp.cloudrunv2.ServiceIamMember`

---

## 5. Environment Variables (Automate with: GCP Secret Manager + Pulumi)

```bash
# Currently set directly on Cloud Run:
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=sb_secret_xxx
OPENAI_API_KEY=sk-xxx
COHERE_API_KEY=xxx
UPSTASH_REDIS_URL=redis://xxx
JWT_SECRET=xxx
INTERNAL_API_KEY=xxx
```

**To automate**: Store in GCP Secret Manager, reference from Cloud Run:
```bash
gcloud secrets create DATABASE_URL --data-file=-
gcloud run services update contextbharat-api --set-secrets=DATABASE_URL=DATABASE_URL:latest
```

---

## 6. Upstash Redis (Automate with: Upstash REST API)

```bash
# Currently manual via console.upstash.com:
# 1. Create database, region: ap-south-1, name: contextbharat
# 2. Copy UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN
```

**To automate**: Upstash has a Terraform provider:
```hcl
resource "upstash_redis_database" "contextbharat" {
  database_name = "contextbharat"
  region        = "ap-south-1"
  tls           = true
}
```

---

## 7. Frontend Deployment (Automate with: Vercel GitHub integration)

```bash
# Currently manual:
cd frontend && vercel --prod

# Env vars set in Vercel dashboard:
NEXT_PUBLIC_API_BASE_URL=https://contextbharat-api-xxx.asia-south1.run.app
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

**To automate**: Connect GitHub repo to Vercel → auto-deploys on push to main.

---

## 8. Custom Domain (Automate with: Cloudflare Terraform provider)

```bash
# Currently not done. Steps:
# 1. Register contextbharat.com on Cloudflare
# 2. Add CNAME: api.contextbharat.com → contextbharat-api-xxx.asia-south1.run.app
# 3. Map domain in Cloud Run: gcloud run domain-mappings create --service=contextbharat-api --domain=api.contextbharat.com
# 4. Add Vercel domain: contextbharat.com → Vercel project
```

---

## Priority Automation Order

1. **GitHub Actions CI/CD** (Week 1) — auto build + deploy on push to main
2. **GCP Secret Manager** (Week 1) — stop storing secrets in env vars
3. **Supabase CLI migrations** (Week 2) — `alembic upgrade head` in CI
4. **Pulumi IaC** (Week 3) — reproducible infrastructure
5. **Custom domain** (Week 3) — api.contextbharat.com
6. **Upstash Terraform** (Week 4) — IaC for Redis
7. **Vercel GitHub integration** (Week 1) — just connect the repo

---

## Credentials Reference (DO NOT COMMIT)

Store these in a password manager, NOT in git:
- GCP Project: contextbharat
- GCP Region: asia-south1 (Mumbai)
- Cloud Run URL: https://contextbharat-api-507218003648.asia-south1.run.app
- Supabase Project: odpnlykpihvdujclaaut
- Supabase Region: ap-south-1 (Mumbai)
- Artifact Registry: asia-south1-docker.pkg.dev/contextbharat/contextbharat
