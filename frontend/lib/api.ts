/**
 * API client for the Context Bharat backend.
 * Used by React components to fetch library data.
 */

/** Use same-origin proxy in browser to avoid CORS; direct URL on server. */
const API_BASE =
  typeof window !== "undefined"
    ? "/api"
    : (process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://contextbharat-api-507218003648.asia-south1.run.app");

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

/**
 * Fetch the number of indexed libraries that have actual documentation chunks.
 * The API's `total` field reflects per-page count, not DB total, so we fetch
 * all libraries and count those with chunk_count > 0.
 * Returns the count as a number, or null if the API is unreachable.
 */
export async function getLibraryCount(): Promise<number | null> {
  try {
    const response = await fetch(`${API_BASE}/v1/libraries?limit=200`);
    if (!response.ok) return null;
    const data = await response.json();
    const libraries: Library[] = data.libraries ?? [];
    // Count only libraries that have been indexed (chunk_count > 0)
    const withDocs = libraries.filter((lib) => lib.chunk_count > 0).length;
    return withDocs > 0 ? withDocs : libraries.length || null;
  } catch {
    return null;
  }
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
