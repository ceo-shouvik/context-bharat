# Context Bharat 🇮🇳

> The documentation layer India's developers deserved. Razorpay, Zerodha Kite, ONDC, UPI, GST — instantly in your AI coding assistant.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![npm version](https://img.shields.io/npm/v/@contextbharat/mcp.svg)](https://www.npmjs.com/package/@contextbharat/mcp)

---

## What Is This?

Context Bharat is an MCP (Model Context Protocol) server that injects up-to-date Indian API documentation directly into Claude, Cursor, VS Code, and any MCP-compatible AI coding tool.

**The problem:** Context7 (the global leader) indexes 9,000+ libraries — but zero Indian APIs. No Razorpay, no ONDC, no Zerodha, no UPI specs. Indian developers were building blind.

**The fix:** We built the missing layer — a documentation server that handles PDFs, government portals, regional languages, and the 100+ APIs that Indian developers actually use.

---

## Quickstart (60 seconds)

### Claude Desktop

```json
// Add to ~/.claude.json
{
  "mcpServers": {
    "contextbharat": {
      "url": "https://mcp.contextbharat.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" }
    }
  }
}
```

### Cursor

```json
// Add to ~/.cursor/mcp.json
{
  "contextbharat": {
    "command": "npx",
    "args": ["-y", "@contextbharat/mcp", "--api-key", "YOUR_API_KEY"]
  }
}
```

### Usage

In any prompt, add `use contextbharat`:

```
How do I create a Razorpay payment link? use contextbharat
How do I place a market order with Zerodha Kite? use contextbharat
What is the ONDC buyer app flow? use contextbharat
```

Get a free API key at [contextbharat.com/dashboard](https://contextbharat.com/dashboard)

---

## Libraries Indexed

**Indian Fintech:** Razorpay, Cashfree, Juspay, PayU, Setu, Paytm PG, PhonePe Business

**India Stack / DPI:** ONDC Protocol, UPI/NPCI, Account Aggregator, GSTN, DigiLocker, Bhashini

**Trading:** Zerodha Kite API, Upstox API, AngelOne SmartAPI, Groww, Dhan, Fyers

**Enterprise India:** Zoho CRM/Books, Frappe/ERPNext, Tally Prime, SAP B1, Freshworks

**Global:** React, Next.js, FastAPI, Django, Flutter, Spring Boot, Supabase, PostgreSQL + 150 more

[See full catalog →](knowledge-base/api-catalog.md)

---

## Repository Structure

```
context-bharat/
├── CLAUDE.md              ← Claude Code instructions (start here)
├── backend/               ← Python FastAPI + ingestion pipeline
├── mcp-server/            ← TypeScript MCP server (forked from upstash/context7)
├── frontend/              ← Next.js 15 dashboard
├── docs/                  ← Development documentation
├── knowledge-base/        ← Technical deep-dives
├── website/               ← Marketing copy
└── docker-compose.yml     ← Local dev infrastructure
```

---

## Development Setup

```bash
# Prerequisites: Node.js 20+, Python 3.12+, Docker

git clone https://github.com/contextbharat/context-bharat.git
cd context-bharat

# Install all dependencies
pnpm install
cd backend && pip install -r requirements.txt && cd ..

# Start local infrastructure (Postgres + pgvector + Redis)
docker compose up -d

# Copy environment variables
cp .env.example .env
# Edit .env — add OPENAI_API_KEY at minimum

# Start all services
pnpm run dev:all

# Run tests
make test
```

Full setup guide: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## Contributing

The best contribution is adding a new Indian API to the index. It takes ~15 minutes.

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for the full guide.

**Most wanted libraries (unindexed):**
- [ ] ABDM Health APIs
- [ ] Account Aggregator (Sahamati)
- [ ] Tally Prime API
- [ ] Any trading API not yet covered

---

## Architecture

Context Bharat = MCP client (forked, MIT) + custom backend (proprietary).

- **MCP Server:** TypeScript, forked from `upstash/context7`
- **Backend API:** Python / FastAPI on Railway
- **Vector DB:** pgvector on Supabase → Qdrant at scale
- **Ingestion:** Crawl4AI + Tesseract OCR + LlamaIndex
- **Translations:** Sarvam AI Mayura (22 Indian languages)

[Full architecture →](knowledge-base/architecture.md)

---

## Credit

The MCP client layer is forked from [upstash/context7](https://github.com/upstash/context7) under MIT License. The backend, ingestion pipeline, vector index, and India-specific features are built by the Context Bharat team.

---

## License

MCP client: Apache 2.0
Backend: Proprietary

---

Built with ❤️ in India.
