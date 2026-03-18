/**
 * HTTP client for the Context Bharat backend API.
 * Called by MCP tool handlers.
 */
import { config } from "./config.js";

export interface ResolveLibraryParams {
  query: string;
  libraryName: string;
}

export interface ResolveLibraryResult {
  libraryId: string;
  name: string;
  description?: string;
  versions: string[];
  tags: string[];
  confidence: number;
}

export interface QueryDocsParams {
  libraryId: string;
  query: string;
  tokenBudget?: number;
  language?: string;
}

export interface QueryDocsResult {
  docs: string;
  libraryId: string;
  libraryName: string;
  sources: string[];
  freshnessScore?: number;
  language: string;
  tokenCount: number;
}

class BackendClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;

  constructor() {
    this.baseUrl = config.apiBaseUrl.replace(/\/$/, "");
    this.apiKey = config.apiKey;
  }

  private get authHeaders(): Record<string, string> {
    return this.apiKey
      ? { Authorization: `Bearer ${this.apiKey}` }
      : {};
  }

  async resolveLibrary(params: ResolveLibraryParams): Promise<ResolveLibraryResult> {
    const response = await this.post<ResolveLibraryResult>("/v1/libraries/resolve", {
      query: params.query,
      library_name: params.libraryName,
    });
    return response;
  }

  async queryDocs(params: QueryDocsParams): Promise<QueryDocsResult> {
    const response = await this.post<QueryDocsResult>("/v1/docs/query", {
      library_id: params.libraryId,
      query: params.query,
      token_budget: params.tokenBudget ?? config.defaultTokenBudget,
      language: params.language ?? "en",
    });
    return response;
  }

  async listLibraries(category?: string): Promise<{ libraries: ResolveLibraryResult[]; total: number }> {
    const url = category
      ? `${this.baseUrl}/v1/libraries?category=${encodeURIComponent(category)}`
      : `${this.baseUrl}/v1/libraries`;
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json", ...this.authHeaders },
      signal: AbortSignal.timeout(config.requestTimeoutMs),
    });
    if (!response.ok) {
      throw new BackendError(response.status, await response.text());
    }
    return response.json();
  }

  private async post<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.authHeaders,
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(config.requestTimeoutMs),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new BackendError(response.status, errorText);
    }

    return response.json() as Promise<T>;
  }
}

export class BackendError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: string,
  ) {
    super(`Backend API error ${status}: ${body}`);
    this.name = "BackendError";
  }
}

export const backendClient = new BackendClient();
