# Context Bharat — Makefile
# Run `make help` to see all commands

.PHONY: help dev test lint format clean install setup ingest

# ─── Help ───────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "Context Bharat — Available Commands"
	@echo "════════════════════════════════════"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          Install all dependencies + start local infra"
	@echo "  make install        Install dependencies only"
	@echo "  make infra-up       Start Postgres + Redis (Docker)"
	@echo "  make infra-down     Stop local infrastructure"
	@echo "  make migrate        Run database migrations"
	@echo ""
	@echo "Development:"
	@echo "  make dev            Start all services (backend + mcp + frontend)"
	@echo "  make dev-backend    Start FastAPI backend only"
	@echo "  make dev-mcp        Start MCP server only"
	@echo "  make dev-frontend   Start Next.js frontend only"
	@echo "  make dev-worker     Start Celery worker only"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests (unit + integration)"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-int       Run integration tests only"
	@echo "  make test-mcp       Run MCP server tests"
	@echo "  make test-e2e       Run end-to-end tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run all linters"
	@echo "  make format         Auto-format all code"
	@echo "  make typecheck      Run type checks"
	@echo ""
	@echo "Ingestion:"
	@echo "  make ingest LIB=razorpay         Ingest a specific library"
	@echo "  make ingest-dry LIB=razorpay     Dry run (preview only)"
	@echo "  make ingest-all                  Ingest all libraries"
	@echo "  make ingest-indian               Ingest Indian fintech + DPI libs"
	@echo ""
	@echo "MCP Setup (for developers):"
	@echo "  make setup-github-mcp         Set up GitHub MCP with your PAT"
	@echo "  make setup-contextbharat-mcp  Set up Context Bharat MCP"
	@echo "  make setup-all-mcp            Set up all MCP servers at once"
	@echo ""
	@echo "Utilities:"
	@echo "  make query LIB=razorpay Q='payment link'   Test a query"
	@echo "  make translate LIB=razorpay LANG=hi        Translate to Hindi"
	@echo "  make clean          Clean build artifacts"
	@echo ""

# ─── Setup ──────────────────────────────────────────────────────────────────
setup: install infra-up migrate
	@echo "✅ Setup complete. Run 'make dev' to start all services."

install:
	@echo "Installing dependencies..."
	pnpm install
	cd backend && pip install -r requirements.txt
	@echo "✅ Dependencies installed."

infra-up:
	@echo "Starting local infrastructure..."
	docker compose up -d
	@echo "✅ Postgres (port 5432) and Redis (port 6379) running."

infra-down:
	docker compose down

infra-reset:
	docker compose down -v
	docker compose up -d

migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head
	@echo "✅ Migrations complete."

migrate-create:
	@echo "Creating new migration: $(MSG)"
	cd backend && alembic revision --autogenerate -m "$(MSG)"

# ─── Development ────────────────────────────────────────────────────────────
dev:
	pnpm run dev:all

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-mcp:
	cd mcp-server && pnpm dev

dev-frontend:
	cd frontend && pnpm dev

dev-worker:
	cd backend && celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2

dev-beat:
	cd backend && celery -A app.tasks.celery_app beat --loglevel=info

# ─── Testing ────────────────────────────────────────────────────────────────
test: test-unit test-int test-mcp

test-unit:
	@echo "Running unit tests..."
	cd backend && pytest tests/unit -v --cov=app --cov-report=term-missing

test-int:
	@echo "Running integration tests..."
	cd backend && pytest tests/integration -v

test-mcp:
	@echo "Running MCP server tests..."
	cd mcp-server && pnpm test

test-e2e:
	@echo "Running end-to-end tests..."
	cd backend && pytest tests/e2e -v

test-frontend:
	cd frontend && pnpm test

# ─── Code Quality ───────────────────────────────────────────────────────────
lint:
	@echo "Linting Python..."
	cd backend && ruff check .
	@echo "Linting TypeScript (MCP)..."
	cd mcp-server && pnpm lint
	@echo "Linting TypeScript (Frontend)..."
	cd frontend && pnpm lint

format:
	@echo "Formatting Python..."
	cd backend && ruff format .
	@echo "Formatting TypeScript (MCP)..."
	cd mcp-server && pnpm format
	@echo "Formatting TypeScript (Frontend)..."
	cd frontend && pnpm format

typecheck:
	@echo "Type checking MCP server..."
	cd mcp-server && pnpm typecheck
	@echo "Type checking frontend..."
	cd frontend && pnpm typecheck

# ─── Ingestion ──────────────────────────────────────────────────────────────
ingest:
	@if [ -z "$(LIB)" ]; then echo "Usage: make ingest LIB=razorpay"; exit 1; fi
	cd backend && python scripts/ingest.py --library $(LIB)

ingest-dry:
	@if [ -z "$(LIB)" ]; then echo "Usage: make ingest-dry LIB=razorpay"; exit 1; fi
	cd backend && python scripts/ingest.py --library $(LIB) --dry-run

ingest-force:
	@if [ -z "$(LIB)" ]; then echo "Usage: make ingest-force LIB=razorpay"; exit 1; fi
	cd backend && python scripts/ingest.py --library $(LIB) --force

ingest-all:
	cd backend && python scripts/ingest.py --all

ingest-indian:
	cd backend && python scripts/ingest.py --category indian-fintech
	cd backend && python scripts/ingest.py --category india-dpi
	cd backend && python scripts/ingest.py --category indian-trading

# ─── Utilities ──────────────────────────────────────────────────────────────
query:
	@if [ -z "$(LIB)" ] || [ -z "$(Q)" ]; then echo "Usage: make query LIB=razorpay Q='payment link'"; exit 1; fi
	cd backend && python scripts/test_query.py --library $(LIB) --query "$(Q)"

translate:
	@if [ -z "$(LIB)" ] || [ -z "$(LANG)" ]; then echo "Usage: make translate LIB=razorpay LANG=hi"; exit 1; fi
	cd backend && python scripts/translate.py --library $(LIB) --lang $(LANG)

mcp-inspect:
	cd mcp-server && npx @modelcontextprotocol/inspector dist/index.js

setup-github-mcp:
	@bash tools/setup-github-mcp.sh

setup-contextbharat-mcp:
	@bash tools/setup-contextbharat-mcp.sh

setup-all-mcp:
	@bash tools/setup-all-mcp.sh

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name dist -not -path "*/node_modules/*" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete
	@echo "✅ Cleaned build artifacts."
