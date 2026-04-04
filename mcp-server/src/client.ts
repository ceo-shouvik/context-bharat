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
    const raw = await this.post<Record<string, unknown>>("/v1/libraries/resolve", {
      query: params.query,
      library_name: params.libraryName,
    });
    return {
      libraryId: (raw.library_id ?? raw.libraryId) as string,
      name: raw.name as string,
      description: raw.description as string | undefined,
      versions: (raw.versions ?? []) as string[],
      tags: (raw.tags ?? []) as string[],
      confidence: (raw.confidence ?? 0) as number,
    };
  }

  async queryDocs(params: QueryDocsParams): Promise<QueryDocsResult> {
    const raw = await this.post<Record<string, unknown>>("/v1/docs/query", {
      library_id: params.libraryId,
      query: params.query,
      token_budget: params.tokenBudget ?? config.defaultTokenBudget,
      language: params.language ?? "en",
    });
    return {
      docs: (raw.docs ?? "") as string,
      libraryId: (raw.library_id ?? raw.libraryId ?? "") as string,
      libraryName: (raw.library_name ?? raw.libraryName ?? "") as string,
      sources: (raw.sources ?? []) as string[],
      freshnessScore: (raw.freshness_score ?? raw.freshnessScore) as number | undefined,
      language: (raw.language ?? "en") as string,
      tokenCount: (raw.token_count ?? raw.tokenCount ?? 0) as number,
    };
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
    return response.json() as Promise<{ libraries: ResolveLibraryResult[]; total: number }>;
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
