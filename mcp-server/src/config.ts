/**
 * MCP Server configuration.
 * Reads environment variables at startup.
 */
export const config = {
  /** Backend API base URL */
  apiBaseUrl: process.env.CONTEXTBHARAT_API_BASE_URL ?? "https://contextbharat.bachao.ai",
  /** API key for authentication — optional, uses free tier if absent */
  apiKey: process.env.CONTEXTBHARAT_API_KEY ?? "",
  /** Default token budget for query-docs */
  defaultTokenBudget: 5000,
  /** Request timeout in milliseconds */
  requestTimeoutMs: 10_000,
  /** Server version */
  version: "0.1.0",
} as const;
