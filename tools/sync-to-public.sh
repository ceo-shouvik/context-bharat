#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Syncs public files from the full repo to the public GitHub repo.
# Run from the full repo root: bash tools/sync-to-public.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

FULL_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PUBLIC_REPO="$FULL_REPO/../context-bharat-public"

if [ ! -d "$PUBLIC_REPO/.git" ]; then
    echo "ERROR: Public repo not found at $PUBLIC_REPO"
    echo "Run: mkdir -p $PUBLIC_REPO && cd $PUBLIC_REPO && git init && git remote add origin https://github.com/shouvikfullstack/context-bharat.git"
    exit 1
fi

echo "==> Syncing public files from $FULL_REPO to $PUBLIC_REPO"

# Clean the public repo (except .git)
find "$PUBLIC_REPO" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

# ─── Root files (public) ─────────────────────────────────────────────────────
cp "$FULL_REPO/CLAUDE.md" "$PUBLIC_REPO/"
cp "$FULL_REPO/README.md" "$PUBLIC_REPO/"
cp "$FULL_REPO/Makefile" "$PUBLIC_REPO/"
cp "$FULL_REPO/docker-compose.yml" "$PUBLIC_REPO/"
cp "$FULL_REPO/package.json" "$PUBLIC_REPO/"
cp "$FULL_REPO/pnpm-workspace.yaml" "$PUBLIC_REPO/"
cp "$FULL_REPO/tsconfig.json" "$PUBLIC_REPO/"
cp "$FULL_REPO/.env.example" "$PUBLIC_REPO/" 2>/dev/null || true

# ─── MCP Server (full — Apache 2.0) ──────────────────────────────────────────
rsync -a --exclude='node_modules' "$FULL_REPO/mcp-server/" "$PUBLIC_REPO/mcp-server/"

# ─── Tools (full — Apache 2.0) ───────────────────────────────────────────────
rsync -a "$FULL_REPO/tools/" "$PUBLIC_REPO/tools/"

# ─── Docs (public subset) ────────────────────────────────────────────────────
mkdir -p "$PUBLIC_REPO/docs"
for f in philosophy.md decisions.md design-patterns.md domain-language.md style-guide.md CONTRIBUTING.md github-mcp-setup.md index.md; do
    cp "$FULL_REPO/docs/$f" "$PUBLIC_REPO/docs/" 2>/dev/null || true
done
# EXCLUDE: pricing-strategy.md, deployment-plan.md, manual-deployment-steps.md

# ─── Knowledge base (public subset) ──────────────────────────────────────────
mkdir -p "$PUBLIC_REPO/knowledge-base"
cp "$FULL_REPO/knowledge-base/api-catalog.md" "$PUBLIC_REPO/knowledge-base/"
cp "$FULL_REPO/knowledge-base/mcp-server.md" "$PUBLIC_REPO/knowledge-base/"
# EXCLUDE: architecture.md, infra.md, roadmap.md, ingestion-pipeline.md

# ─── Website content (public) ────────────────────────────────────────────────
rsync -a "$FULL_REPO/website/" "$PUBLIC_REPO/website/"

# ─── Backend (public subset only) ────────────────────────────────────────────
mkdir -p "$PUBLIC_REPO/backend/config/libraries"
mkdir -p "$PUBLIC_REPO/backend/app/ingestion"
mkdir -p "$PUBLIC_REPO/backend/app/models"

# Library configs — the community contribution target
rsync -a "$FULL_REPO/backend/config/libraries/" "$PUBLIC_REPO/backend/config/libraries/" 2>/dev/null || true

# Base crawler interface — so community knows the contract
cp "$FULL_REPO/backend/app/ingestion/base.py" "$PUBLIC_REPO/backend/app/ingestion/" 2>/dev/null || true

# Pydantic schemas — public for SDK builders
cp "$FULL_REPO/backend/app/models/schemas.py" "$PUBLIC_REPO/backend/app/models/" 2>/dev/null || true

# requirements.txt (so people can see dependencies)
cp "$FULL_REPO/backend/requirements.txt" "$PUBLIC_REPO/backend/" 2>/dev/null || true

# Backend README
cat > "$PUBLIC_REPO/backend/README.md" << 'BACKEND_README'
# Backend

The full backend (ingestion pipeline, API, services, database) is proprietary and lives in a private repository.

## What's here (public)

- `config/libraries/` — Library JSON configs. **This is where community contributions go.** See [docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md).
- `app/ingestion/base.py` — Base crawler interface (so you know the contract).
- `app/models/schemas.py` — Pydantic request/response schemas (for SDK builders).
- `requirements.txt` — Python dependencies.

## Want to contribute?

The easiest contribution is adding a new Indian API library config. See [docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md).
BACKEND_README

# ─── Frontend (public pages only) ────────────────────────────────────────────
mkdir -p "$PUBLIC_REPO/frontend/app/setup/github-mcp"
mkdir -p "$PUBLIC_REPO/frontend/app/docs"
mkdir -p "$PUBLIC_REPO/frontend/app/pricing"
mkdir -p "$PUBLIC_REPO/frontend/components"
mkdir -p "$PUBLIC_REPO/frontend/lib"
mkdir -p "$PUBLIC_REPO/frontend/public/logos"

# Config files
for f in package.json tsconfig.json tailwind.config.ts postcss.config.js next.config.ts vitest.config.ts; do
    cp "$FULL_REPO/frontend/$f" "$PUBLIC_REPO/frontend/" 2>/dev/null || true
done

# Root layout + globals
cp "$FULL_REPO/frontend/app/layout.tsx" "$PUBLIC_REPO/frontend/app/"
cp "$FULL_REPO/frontend/app/globals.css" "$PUBLIC_REPO/frontend/app/"

# Public pages
cp "$FULL_REPO/frontend/app/page.tsx" "$PUBLIC_REPO/frontend/app/"                          # Landing page
cp "$FULL_REPO/frontend/app/docs/page.tsx" "$PUBLIC_REPO/frontend/app/docs/"                # Docs page
cp "$FULL_REPO/frontend/app/setup/page.tsx" "$PUBLIC_REPO/frontend/app/setup/"              # Setup tools hub
cp "$FULL_REPO/frontend/app/setup/github-mcp/page.tsx" "$PUBLIC_REPO/frontend/app/setup/github-mcp/"  # GitHub MCP detail
cp "$FULL_REPO/frontend/app/pricing/page.tsx" "$PUBLIC_REPO/frontend/app/pricing/" 2>/dev/null || true

# Public components
cp "$FULL_REPO/frontend/components/live-playground.tsx" "$PUBLIC_REPO/frontend/components/" 2>/dev/null || true
cp "$FULL_REPO/frontend/components/logo-slider.tsx" "$PUBLIC_REPO/frontend/components/" 2>/dev/null || true
cp "$FULL_REPO/frontend/components/feature-cards.tsx" "$PUBLIC_REPO/frontend/components/" 2>/dev/null || true

# Public lib (API client only, not supabase/admin)
cp "$FULL_REPO/frontend/lib/api.ts" "$PUBLIC_REPO/frontend/lib/" 2>/dev/null || true

# Logos
rsync -a "$FULL_REPO/frontend/public/logos/" "$PUBLIC_REPO/frontend/public/logos/" 2>/dev/null || true

# Frontend README for excluded parts
cat > "$PUBLIC_REPO/frontend/README.md" << 'FRONTEND_README'
# Frontend

Public pages for contextbharat.com. The dashboard, admin, and auth pages are in the private repository.

## What's here (public)

- Landing page (`app/page.tsx`)
- Docs / setup guide (`app/docs/`)
- MCP setup tools (`app/setup/`)
- Pricing page (`app/pricing/`)
- Public components (live playground, logo slider)

## What's private

- Dashboard (`app/(dashboard)/`)
- Admin panel (`app/admin/`)
- Auth pages (`app/(auth)/`)
- API key manager, usage charts, query tester
FRONTEND_README

# ─── Claude rules (public) ───────────────────────────────────────────────────
rsync -a "$FULL_REPO/.claude/" "$PUBLIC_REPO/.claude/" 2>/dev/null || true

# ─── .gitignore ──────────────────────────────────────────────────────────────
cat > "$PUBLIC_REPO/.gitignore" << 'GITIGNORE'
node_modules/
dist/
.next/
.env
.env.local
.env.production
__pycache__/
*.pyc
.pytest_cache/
.coverage
.venv/
*.egg-info/
GITIGNORE

# ─── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "==> Sync complete. Files in public repo:"
echo ""
cd "$PUBLIC_REPO"
find . -not -path './.git/*' -not -path './node_modules/*' -not -name '.git' -type f | sort | head -60
FILE_COUNT=$(find . -not -path './.git/*' -not -path './node_modules/*' -not -name '.git' -type f | wc -l)
echo "... ($FILE_COUNT files total)"
echo ""
echo "==> Next: cd $PUBLIC_REPO && git add -A && git commit -m 'initial public release' && git push origin main"
