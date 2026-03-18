# MCP Server

How the MCP server works, how to test it, and how to extend it.

---

## What is MCP?

Model Context Protocol (MCP) is an open standard (JSON-RPC 2.0) for giving AI coding assistants access to external tools and data. When a developer types "use context7india" in Claude or Cursor, the MCP server intercepts the request, fetches the relevant docs from our backend, and injects them into the LLM's context.

MCP transport modes:
- **stdio** — local process, AI client spawns MCP server as subprocess. Used by Claude Desktop, Cursor.
- **Streamable HTTP** — remote server at `mcp.context7india.com/mcp`. Any MCP client can connect.

---

## Our Two Tools

### `resolve-library-id`

Maps a human name to a canonical library ID.

```typescript
// Input
{
  "query": "zerodha trading api",       // What the developer typed
  "libraryName": "zerodha kite"        // Extracted library name
}

// Output
{
  "library_id": "/zerodha/kite-api",
  "name": "Zerodha Kite API",
  "description": "Python/JS trading API for stocks, options, and derivatives",
  "versions": ["3.0", "2.9"],
  "tags": ["trading", "india", "stocks", "zerodha"]
}
```

**Resolution logic:**
1. Exact match on library_id
2. Fuzzy name match (Levenshtein distance)
3. Tag-based search
4. Semantic search on descriptions

### `query-docs`

Retrieves relevant documentation.

```typescript
// Input
{
  "libraryId": "/zerodha/kite-api",
  "query": "how to place a market order",
  "tokenBudget": 5000,
  "language": "en"   // "en" | "hi" | "ta" | "te" | "kn" | "bn"
}

// Output
{
  "docs": "## Placing Orders\n\nUse `kite.place_order()` to place orders...\n\n```python\norder_id = kite.place_order(\n    variety=kite.VARIETY_REGULAR,\n    exchange=kite.EXCHANGE_NSE,\n    tradingsymbol='INFY',\n    transaction_type=kite.TRANSACTION_TYPE_BUY,\n    quantity=1,\n    order_type=kite.ORDER_TYPE_MARKET,\n    product=kite.PRODUCT_CNC\n)\n```",
  "sources": ["https://kite.trade/docs/connect/v3/orders/"],
  "freshness_score": 0.97,
  "library_id": "/zerodha/kite-api"
}
```

---

## Installation for Developers

### Option 1: Remote (easiest)

```json
// In Claude Desktop ~/.claude.json or Cursor settings
{
  "mcpServers": {
    "context7india": {
      "url": "https://mcp.context7india.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### Option 2: Local (faster, works offline)

```bash
npx @context7india/mcp --api-key YOUR_API_KEY
```

Add to Claude Desktop `~/.claude.json`:
```json
{
  "mcpServers": {
    "context7india": {
      "command": "npx",
      "args": ["-y", "@context7india/mcp", "--api-key", "YOUR_API_KEY"]
    }
  }
}
```

### No API Key Mode

```bash
npx @context7india/mcp
# 100 queries/day free, top 30 libraries only
```

---

## Testing the MCP Server Locally

```bash
cd mcp-server

# Build
pnpm build

# Start inspector (interactive MCP testing UI)
npx @modelcontextprotocol/inspector dist/index.js

# The inspector opens at http://localhost:5173
# Test tools:
# 1. resolve-library-id: query="razorpay payment", libraryName="razorpay"
# 2. query-docs: libraryId="/razorpay/razorpay-sdk", query="payment link creation"

# Unit tests
pnpm test

# Integration test (requires local backend running)
CONTEXT7INDIA_API_BASE_URL=http://localhost:8000 pnpm test:integration
```

---

## Extending with New Tools

Add a new tool in `mcp-server/src/tools/`:

```typescript
// mcp-server/src/tools/list-libraries.ts
import { z } from "zod";
import { Tool } from "@modelcontextprotocol/typescript-sdk";
import { backendClient } from "../client";

const ListLibrariesInput = z.object({
  category: z.enum([
    "indian-fintech", "india-dpi", "indian-trading",
    "enterprise-india", "global-framework", "all"
  ]).default("all"),
});

export const listLibrariesTool: Tool = {
  name: "list-libraries",
  description: "List all available libraries in the Context7 India index. Filter by category.",
  inputSchema: ListLibrariesInput,
  async handler(input) {
    return await backendClient.listLibraries({ category: input.category });
  },
};
```

Register in `src/index.ts`:
```typescript
import { listLibrariesTool } from "./tools/list-libraries";
server.addTool(listLibrariesTool);
```

---

## Context7 Compatibility

Our tool names and input schemas are compatible with Context7's API. This means:
- Developers who use Context7 can switch to Context7 India with a URL change
- Community-built integrations (VS Code extensions, Cursor plugins) work with our server
- We can gradually expand beyond Context7's feature set without breaking compatibility
