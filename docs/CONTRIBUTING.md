# Contributing

Welcome. This document explains how to contribute to Context7 India.

---

## How to Add a New Library (Most Common Contribution)

The easiest and most impactful way to contribute is adding a new Indian API or framework to the index.

### Step 1: Check if it already exists

```bash
cat knowledge-base/api-catalog.md | grep -i "your-library-name"
```

Also check the open issues — someone might already be working on it.

### Step 2: Create the library config

Create a new file at `backend/config/libraries/{library-slug}.json`:

```json
{
  "library_id": "/{owner}/{repo}",
  "name": "Human Readable Name",
  "description": "One sentence: what this API does and who uses it.",
  "category": "indian-fintech | india-dpi | indian-trading | enterprise-india | indian-ai | global-framework | saas-cloud",
  "source": {
    "type": "web | github | pdf | multi",
    "urls": ["https://docs.example.com/"],
    "crawl_depth": 3
  },
  "npm_package": "optional-npm-package",
  "pypi_package": "optional-pypi-package",
  "github_repo": "owner/repo",
  "refresh_interval_hours": 24,
  "languages": ["en"],
  "tags": ["relevant", "tags", "here"]
}
```

### Step 3: Add to the API catalog

Add a row to `knowledge-base/api-catalog.md` under the right category.

### Step 4: Test ingestion locally

```bash
cd backend
python scripts/ingest.py --library your-library-slug --dry-run
# Review output — does it look reasonable?
python scripts/ingest.py --library your-library-slug
# Run a test query
python scripts/test_query.py --library your-library-slug --query "authentication"
```

### Step 5: Open a PR

PR title: `feat(catalog): add {Library Name} to index`

PR description should include:
- What the library is and why it's important
- Screenshot or output of `scripts/test_query.py` showing it works
- Any unusual ingestion challenges (e.g., portal auth required, PDF-only)

---

## How to Report a Bug

1. Check [existing issues](https://github.com/context7india/context7-india/issues) first
2. Open a new issue with the bug report template
3. Include: what you expected, what happened, reproduction steps

**For stale documentation bugs:**
Use the "Report stale docs" button in the web dashboard or file an issue with label `stale-docs`. Include the library ID and the incorrect information.

---

## How to Improve Existing Documentation

PR title: `docs({library-slug}): fix incorrect {topic} example`

For major documentation improvements to Indian government APIs — we especially need:
- Better OCR cleanup for scanned NPCI PDFs
- ONDC Beckn Protocol flow examples
- GSTN API error code documentation
- ABDM health API webhook handling examples

---

## Development Setup

```bash
# Clone the repo
git clone https://github.com/context7india/context7-india.git
cd context7-india

# Install all deps
pnpm install
cd backend && pip install -r requirements.txt

# Start local infrastructure
docker compose up -d   # Starts Postgres (pgvector) + Redis

# Copy env file
cp .env.example .env
# Fill in: OPENAI_API_KEY, SUPABASE_URL (use local for dev)

# Start all services
pnpm run dev:all

# Run tests
make test
```

---

## Code Style

See `docs/style-guide.md` for all style rules. The short version:
- Python: Ruff formatter (`cd backend && ruff format .`)
- TypeScript: Prettier (`pnpm format`)
- All tests must pass before PR
- Add tests for new ingestion source types

---

## Community

- Twitter/X: `@context7india`
- GitHub Discussions for questions
- Monthly Document-a-thon events — follow Twitter for announcements
- iSPIRT community for India Stack API discussions
