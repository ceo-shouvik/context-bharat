#!/usr/bin/env node
/**
 * Context7 India — MCP Server
 *
 * Provides AI coding assistants (Claude, Cursor, VS Code) with up-to-date
 * documentation for Indian APIs, government specs, and global frameworks.
 *
 * Tools:
 *   - resolve-library-id: map library name → canonical ID
 *   - query-docs: retrieve relevant documentation chunks
 *
 * Forked from: upstash/context7 (MIT License)
 * Backend: Context7 India proprietary index
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

import { config } from "./config.js";
import {
  resolveLibraryIdHandler,
  resolveLibraryIdSchema,
} from "./tools/resolve-library-id.js";
import { queryDocsHandler, queryDocsSchema } from "./tools/query-docs.js";

const server = new Server(
  {
    name: "context7india",
    version: config.version,
  },
  {
    capabilities: { tools: {} },
  },
);

// ── Tool definitions ──────────────────────────────────────────────────────────

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "resolve-library-id",
      description:
        "Resolve a library or API name to a Context7India-compatible library ID. " +
        "Always call this before query-docs if you only have a library name. " +
        "Supports 100+ Indian APIs (Razorpay, Zerodha, ONDC, UPI, GST) and global frameworks.",
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "The full user query for context",
          },
          libraryName: {
            type: "string",
            description: "The library or API name to resolve",
          },
        },
        required: ["query", "libraryName"],
      },
    },
    {
      name: "query-docs",
      description:
        "Retrieve current documentation for a library. " +
        "Returns relevant Markdown documentation within your token budget. " +
        "Supports Hindi documentation for Indian APIs (language='hi'). " +
        "Use after resolve-library-id to get the libraryId.",
      inputSchema: {
        type: "object",
        properties: {
          libraryId: {
            type: "string",
            description: "Context7India library ID, e.g. /razorpay/razorpay-sdk",
          },
          query: {
            type: "string",
            description: "Developer's specific question or task",
          },
          tokenBudget: {
            type: "number",
            description: "Max tokens to return (default 5000)",
            default: 5000,
          },
          language: {
            type: "string",
            enum: ["en", "hi", "ta", "te", "kn", "bn"],
            description: "Documentation language (default: en)",
            default: "en",
          },
        },
        required: ["libraryId", "query"],
      },
    },
  ],
}));

// ── Tool execution ────────────────────────────────────────────────────────────

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result: string;

    if (name === "resolve-library-id") {
      const input = resolveLibraryIdSchema.parse(args);
      result = await resolveLibraryIdHandler(input);
    } else if (name === "query-docs") {
      const input = queryDocsSchema.parse(args);
      result = await queryDocsHandler(input);
    } else {
      return {
        content: [{ type: "text", text: `Unknown tool: ${name}` }],
        isError: true,
      };
    }

    return {
      content: [{ type: "text", text: result }],
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Error: ${message}` }],
      isError: true,
    };
  }
});

// ── Start server ─────────────────────────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  process.stderr.write(
    `Context7 India MCP server v${config.version} started (stdio)\n`,
  );
}

main().catch((error) => {
  process.stderr.write(`Fatal: ${error}\n`);
  process.exit(1);
});
