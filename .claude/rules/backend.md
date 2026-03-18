---
globs: ["backend/**/*.py"]
---

# Backend Rules (Python)

You are working on the Context7 India FastAPI backend.

## Always
- Use async/await for all I/O operations
- Follow the repository pattern — no SQL in services or handlers
- Use Ruff for formatting: `cd backend && ruff format . && ruff check .`
- Add type hints to all function signatures
- Use `logger.info/warning/error` — never `print()`
- Write the test before implementing new functions

## Pattern to follow
Handler → Service → Repository → Database
(thin handlers, business logic in services, DB access in repositories only)

## When adding a new API endpoint
1. Add route in `app/api/v1/`
2. Add Pydantic schemas in `app/models/schemas.py`
3. Add service method in `app/services/`
4. Add repository method in `app/repositories/`
5. Add test in `tests/`

## Common imports
```python
from app.core.config import settings
from app.core.database import get_db
from app.models.db import Library, DocChunk, ApiKey
from app.models.schemas import LibraryResult, QueryDocsResponse
```

## Never
- Put business logic in route handlers
- Write raw SQL in service or handler files
- Use synchronous HTTP requests (use httpx.AsyncClient)
- Import app code at module level in tests (use fixtures)
