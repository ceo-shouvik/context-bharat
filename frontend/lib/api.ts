/**
 * API client for the Context Bharat backend.
 * Used by React components to fetch library data.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.contextbharat.com";

export interface Library {
  library_id: string;
  name: string;
  description?: string;
  category: string;
  tags: string[];
  freshness_score?: number;
  last_indexed_at?: string;
  chunk_count: number;
}

export async function getLibraries(params?: {
  category?: string;
  q?: string;
  limit?: number;
}): Promise<Library[]> {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.q) qs.set("q", params.q);
  if (params?.limit) qs.set("limit", String(params.limit));

  const response = await fetch(`${API_BASE}/v1/libraries?${qs}`);
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  const data = await response.json();
  return data.libraries;
}

export async function queryDocs(params: {
  libraryId: string;
  query: string;
  tokenBudget?: number;
  language?: string;
  apiKey?: string;
}): Promise<{ docs: string; sources: string[]; freshnessScore?: number }> {
  const response = await fetch(`${API_BASE}/v1/docs/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(params.apiKey ? { Authorization: `Bearer ${params.apiKey}` } : {}),
    },
    body: JSON.stringify({
      library_id: params.libraryId,
      query: params.query,
      token_budget: params.tokenBudget ?? 5000,
      language: params.language ?? "en",
    }),
  });
  if (!response.ok) throw new Error(`Query failed: ${response.status}`);
  const data = await response.json();
  return {
    docs: data.docs,
    sources: data.sources ?? [],
    freshnessScore: data.freshness_score,
  };
}
