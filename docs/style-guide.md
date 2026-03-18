# Style Guide

Formatting and style rules for all code in this repo. Enforced by linters where possible — only rules that require human judgment live here.

---

## Python

### Formatter: Ruff (replaces Black + isort + flake8)

```bash
cd backend && ruff format .    # Format code
cd backend && ruff check .     # Lint
cd backend && ruff check . --fix  # Auto-fix lint issues
```

Config in `backend/pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

### Type Hints

All function signatures must have type hints. Use `from __future__ import annotations` at the top of files for forward references.

```python
# Good
async def get_library(library_id: str) -> Library | None:
    ...

# Bad
async def get_library(library_id):
    ...
```

### Docstrings

Public functions and classes need docstrings. One-line for simple functions, multi-line for complex ones.

```python
def chunk_document(text: str, max_tokens: int = 512) -> list[Chunk]:
    """Split a document into chunks that respect token limits and section boundaries."""
    ...

async def run_full_ingestion(
    library_id: str,
    force_refresh: bool = False,
) -> IngestionResult:
    """
    Run the complete ingestion pipeline for a library.

    Args:
        library_id: Canonical library identifier, e.g. '/razorpay/razorpay-sdk'
        force_refresh: If True, re-index even if docs are fresh.

    Returns:
        IngestionResult with chunk count, errors, and freshness timestamp.

    Raises:
        LibraryNotFoundError: If library_id is not in the config registry.
        IngestionError: If crawling or embedding fails.
    """
    ...
```

### Imports

```python
# Order: stdlib → third-party → local. Ruff handles this automatically.
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Library
from app.services.library_service import LibraryService
```

### No Magic Numbers

```python
# Bad
if hours_since_index > 168:
    ...

# Good
STALENESS_THRESHOLD_HOURS = 168  # 7 days

if hours_since_index > STALENESS_THRESHOLD_HOURS:
    ...
```

### Logging

Use structured logging. Never use `print()` in production code.

```python
import logging
logger = logging.getLogger(__name__)

# Good
logger.info("Starting ingestion", extra={"library_id": library_id, "force": force_refresh})
logger.error("Ingestion failed", extra={"library_id": library_id}, exc_info=True)

# Bad
print(f"Starting ingestion for {library_id}")
```

---

## TypeScript

### Formatter: Prettier + ESLint

```bash
cd mcp-server && pnpm format    # Prettier
cd mcp-server && pnpm lint      # ESLint
cd frontend && pnpm format
cd frontend && pnpm lint
```

Config: `.prettierrc` at root
```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100
}
```

### Types

Always use explicit types. No `any`. Use `unknown` if type is truly unknown, then narrow it.

```typescript
// Good
function parseLibraryId(input: string): LibraryId {
  ...
}

// Bad
function parseLibraryId(input: any): any {
  ...
}
```

### Async/Await

Always use `async/await`. Never raw `.then()` chains.

```typescript
// Good
const docs = await client.getDocs({ libraryId, query });

// Bad
client.getDocs({ libraryId, query }).then((docs) => { ... });
```

### Error Handling

```typescript
// Good — typed errors
class LibraryNotFoundError extends Error {
  constructor(libraryId: string) {
    super(`Library not found: ${libraryId}`);
    this.name = "LibraryNotFoundError";
  }
}

try {
  const result = await resolveLibraryId(name);
} catch (error) {
  if (error instanceof LibraryNotFoundError) {
    // handle not found
  }
  throw error; // re-throw unexpected errors
}
```

---

## SQL / Database

### Migration files

Use Alembic for migrations. Never edit migration files after they've been applied to production.

```bash
cd backend && alembic revision --autogenerate -m "add freshness_score to doc_chunks"
cd backend && alembic upgrade head
cd backend && alembic downgrade -1  # Rollback one migration
```

### Indexes

Add indexes for every column used in WHERE, JOIN, or ORDER BY clauses in hot paths.

```sql
-- Always index these
CREATE INDEX idx_libraries_category ON libraries(category);
CREATE INDEX idx_doc_chunks_library_id ON doc_chunks(library_id);
CREATE INDEX idx_doc_chunks_language ON doc_chunks(language);

-- pgvector index (IVFFlat for MVP)
CREATE INDEX idx_doc_chunks_embedding ON doc_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Never Raw Queries in Application Code

```python
# Good — SQLAlchemy ORM
result = await session.execute(
    select(DocChunk)
    .where(DocChunk.library_id == library_id)
    .order_by(DocChunk.created_at.desc())
    .limit(100)
)

# Only raw SQL in migrations or very specific performance-critical paths,
# documented with a comment explaining why ORM couldn't be used
```

---

## API Design

### Response Envelope

All REST API responses follow this structure:

```json
{
  "data": { ... },
  "meta": {
    "total": 42,
    "freshness_score": 0.95,
    "library_id": "/razorpay/razorpay-sdk"
  }
}
```

Errors:
```json
{
  "error": {
    "code": "LIBRARY_NOT_FOUND",
    "message": "Library /xyz/abc not found in index",
    "details": {}
  }
}
```

### Versioning

All endpoints are prefixed `/v1/`. When breaking changes are needed, add `/v2/` — don't modify `/v1/`.

### Rate Limiting Headers

All API responses include:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1711234567
```

---

## Testing

### Coverage Targets

- Unit tests: 80%+ coverage on `app/services/` and `app/ingestion/`
- Integration tests: All API endpoints have at least one happy-path test
- E2E tests: Complete ingestion + query cycle for Razorpay and one govt API

### Test File Naming

Mirror the source file structure:
```
backend/app/services/library_service.py
backend/tests/unit/services/test_library_service.py

backend/app/ingestion/pdf_crawler.py
backend/tests/unit/ingestion/test_pdf_crawler.py
```

### Test Fixtures

Common fixtures in `backend/tests/conftest.py`. Database fixtures use transactions that roll back after each test.

```python
@pytest.fixture
async def test_library(test_db: AsyncSession) -> Library:
    """A seeded Razorpay library for testing."""
    library = Library(
        library_id="/razorpay/razorpay-sdk",
        name="Razorpay",
        category="indian-fintech",
    )
    test_db.add(library)
    await test_db.commit()
    return library
```

---

## Git

### Branch Naming
```
feat/ingestion-pdf-ocr
fix/mcp-server-timeout
docs/add-gstn-api-catalog
chore/update-crawl4ai-2.5
test/integration-ondc-ingestion
```

### Commit Messages
`type(scope): imperative description`

Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`
Scopes: `ingestion`, `mcp-server`, `frontend`, `api`, `db`, `infra`

```
feat(ingestion): add PDF OCR pipeline for scanned government docs
fix(mcp-server): handle timeout when backend API is unreachable
docs(api-catalog): add Zerodha Kite API documentation entry
chore(deps): update LlamaIndex to 0.12.0
```

### PR Rules

- One feature / one fix per PR
- Must pass all tests (`make test`)
- Must have a description explaining what and why
- Breaking changes require a migration note in PR description
- Merge via squash (clean history)
