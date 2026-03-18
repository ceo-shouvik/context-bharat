import type { ClientOptions, Library, QueryDocsParams, QueryDocsResult } from "./types.js";

export class ContextBharatClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly timeoutMs: number;

  constructor(options: ClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? "https://api.contextbharat.com").replace(/\/$/, "");
    this.apiKey = options.apiKey ?? "";
    this.timeoutMs = options.timeoutMs ?? 10_000;
  }

  async queryDocs(params: QueryDocsParams): Promise<QueryDocsResult> {
    const response = await this.post<QueryDocsResult>("/v1/docs/query", {
      library_id: params.libraryId,
      query: params.query,
      token_budget: params.tokenBudget ?? 5000,
      language: params.language ?? "en",
    });
    return response;
  }

  async listLibraries(category?: string): Promise<Library[]> {
    const url = category
      ? `${this.baseUrl}/v1/libraries?category=${encodeURIComponent(category)}`
      : `${this.baseUrl}/v1/libraries`;
    const res = await fetch(url, {
      headers: this.headers,
      signal: AbortSignal.timeout(this.timeoutMs),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const data = await res.json();
    return data.libraries;
  }

  private get headers(): Record<string, string> {
    return {
      "Content-Type": "application/json",
      ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
    };
  }

  private async post<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(this.timeoutMs),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}: ${await res.text()}`);
    return res.json() as Promise<T>;
  }
}
