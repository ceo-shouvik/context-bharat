# Knowledge Base Index

Start here. This file maps every document in the knowledge base and tells you when to read it.

---

## When You're New to the Project

Read in this order:
1. `/CLAUDE.md` — the master Claude Code instruction file (you are likely already reading it)
2. `docs/philosophy.md` — why we build the way we build
3. `docs/domain-language.md` — the vocabulary of this codebase
4. `knowledge-base/architecture.md` — how all the pieces connect

---

## When You're Adding a New Library

1. `knowledge-base/api-catalog.md` — find the right category and template
2. `docs/design-patterns.md` → "Configuration Pattern" — JSON config format
3. `knowledge-base/ingestion-pipeline.md` — how the crawling works
4. `CLAUDE.md` → "Common Tasks → Add a new library" — step-by-step

---

## When You're Working on Ingestion

- `knowledge-base/ingestion-pipeline.md` — full pipeline architecture
- `docs/design-patterns.md` → "Ingestion Pipeline Pattern"
- `docs/decisions.md` → ADR-004 (why Crawl4AI + Tesseract)

---

## When You're Working on the MCP Server

- `knowledge-base/mcp-server.md` — tool definitions, transport, testing
- `docs/design-patterns.md` → "TypeScript / MCP Server Patterns"
- `docs/decisions.md` → ADR-001 (why we forked Context7), ADR-002 (why TypeScript)

---

## When You're Working on the Backend API

- `docs/design-patterns.md` → "Backend Patterns (Python)"
- `docs/decisions.md` → ADR-003 (pgvector), ADR-009 (Celery)
- `docs/style-guide.md` → Python section

---

## When You're Working on Infrastructure

- `knowledge-base/infra.md` — full infra setup, costs, scaling
- `docs/decisions.md` → ADR-007 (Railway), ADR-005 (embeddings)

---

## When You're Building the Frontend

- `docs/design-patterns.md` → "Frontend Patterns"
- `docs/style-guide.md` → TypeScript section
- `website/content.md` — marketing copy for the public site

---

## When You're Making a Big Decision

1. Check `docs/decisions.md` — is there an existing ADR?
2. If not, add a new ADR at the bottom of `docs/decisions.md`
3. Discuss in PR before implementing

---

## Document Map

| File | What it covers |
|------|---------------|
| `/CLAUDE.md` | Claude Code instructions, commands, quick reference |
| `docs/philosophy.md` | Core principles, priorities, mindset |
| `docs/decisions.md` | Architecture Decision Records (ADRs) |
| `docs/design-patterns.md` | Code patterns for Python, TypeScript, SQL, API design |
| `docs/domain-language.md` | Glossary: India Stack, fintech terms, system terms |
| `docs/style-guide.md` | Code formatting, naming conventions, testing rules |
| `docs/CONTRIBUTING.md` | How to contribute: library PRs, bug reports, features |
| `knowledge-base/architecture.md` | Full system architecture diagram and component breakdown |
| `knowledge-base/ingestion-pipeline.md` | Crawling, OCR, chunking, embedding, upsert pipeline |
| `knowledge-base/mcp-server.md` | MCP server implementation, tools, transport, testing |
| `knowledge-base/api-catalog.md` | All supported libraries and their ingestion status |
| `knowledge-base/infra.md` | Infrastructure: Railway, Supabase, Vercel, costs, scaling |
| `knowledge-base/roadmap.md` | What we're building, current sprint, backlog |
| `website/content.md` | Marketing site copy, messaging, SEO metadata |
| `.env.example` | All environment variables with descriptions |
