// eslint-disable-next-line @typescript-eslint/no-require-imports
const pkg = require("../package.json") as { version: string };

/**
 * MCP Server configuration.
 * Reads environment variables at startup.
 */
export const config = {
  /** Backend API base URL */
  apiBaseUrl: process.env.CONTEXTBHARAT_API_BASE_URL ?? "https://api.contextbharat.com",
  /** API key for authentication — optional, uses free tier if absent */
  apiKey: process.env.CONTEXTBHARAT_API_KEY ?? "",
  /** Default token budget for query-docs */
  defaultTokenBudget: 5000,
  /** Request timeout in milliseconds */
  requestTimeoutMs: 10_000,
  /** Server version — sourced from package.json, never drifts */
  version: pkg.version,
} as const;
