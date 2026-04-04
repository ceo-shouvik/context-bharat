#!/usr/bin/env node
/**
 * Context Bharat — MCP Server
 *
 * Provides AI coding assistants (Claude, Cursor, VS Code) with up-to-date
 * documentation for Indian APIs, government specs, and global frameworks.
 *
 * Tools:
 *   - resolve-library-id: map library name → canonical ID
 *   - query-docs: retrieve relevant documentation chunks
 *
 * Transport:
 *   - PORT env var set  → HTTP Streamable (for Cloud Run / remote hosting)
 *   - PORT env var unset → stdio (for local npx usage)
 *
 * Forked from: upstash/context7 (MIT License)
 * Backend: Context Bharat proprietary index
 */
import http from "node:http";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
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

function createServer(): Server {
  const server = new Server(
    {
      name: "contextbharat",
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
          "Resolve a library or API name to a ContextBharat-compatible library ID. " +
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
              description: "ContextBharat library ID, e.g. /razorpay/razorpay-sdk",
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

  return server;
}

// ── HTTP mode (Cloud Run) ─────────────────────────────────────────────────────

async function startHttpServer(port: number): Promise<void> {
  // Stateless transport: each POST /mcp gets a fresh transport+server pair.
  // This is the simplest approach for Cloud Run where instances can be recycled.
  const httpServer = http.createServer(async (req, res) => {
    // Health check endpoint — required by Cloud Run
    if (req.method === "GET" && req.url === "/health") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "ok", version: config.version }));
      return;
    }

    // MCP endpoint
    if (req.url === "/mcp" || req.url === "/") {
      // Collect request body
      const chunks: Buffer[] = [];
      req.on("data", (chunk: Buffer) => chunks.push(chunk));
      await new Promise<void>((resolve) => req.on("end", resolve));
      const body = Buffer.concat(chunks).toString("utf-8");

      let parsedBody: unknown;
      try {
        parsedBody = body ? JSON.parse(body) : undefined;
      } catch {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Invalid JSON body" }));
        return;
      }

      // Create a fresh server + transport per request (stateless)
      const server = createServer();
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined, // stateless
      });

      await server.connect(transport);
      await transport.handleRequest(req, res, parsedBody);
      return;
    }

    // 404 for everything else
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Not found" }));
  });

  await new Promise<void>((resolve, reject) => {
    httpServer.listen(port, "0.0.0.0", () => resolve());
    httpServer.on("error", reject);
  });

  process.stderr.write(
    `Context Bharat MCP server v${config.version} started (HTTP on :${port})\n`,
  );
}

// ── stdio mode (local npx) ────────────────────────────────────────────────────

async function startStdioServer(): Promise<void> {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  process.stderr.write(
    `Context Bharat MCP server v${config.version} started (stdio)\n`,
  );
}

// ── Entrypoint ────────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  const portEnv = process.env.PORT;
  if (portEnv) {
    const port = parseInt(portEnv, 10);
    if (isNaN(port)) {
      throw new Error(`Invalid PORT env var: "${portEnv}"`);
    }
    await startHttpServer(port);
  } else {
    await startStdioServer();
  }
}

main().catch((error) => {
  process.stderr.write(`Fatal: ${error}\n`);
  process.exit(1);
});
