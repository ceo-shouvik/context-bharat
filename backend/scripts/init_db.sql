-- Initial DB setup for local development
-- This runs automatically via Docker entrypoint

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search

-- Full-text search index (BM25-style)
-- Will also be created by Alembic migrations but needed for local dev

COMMENT ON DATABASE context7india IS 'Context7 India — vector documentation database';
