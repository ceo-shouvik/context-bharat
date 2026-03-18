export interface ClientOptions {
  apiKey?: string;
  baseUrl?: string;
  timeoutMs?: number;
}

export interface QueryDocsParams {
  libraryId: string;
  query: string;
  tokenBudget?: number;
  language?: "en" | "hi" | "ta" | "te" | "kn" | "bn";
}

export interface QueryDocsResult {
  docs: string;
  libraryId: string;
  libraryName: string;
  sources: string[];
  freshnessScore?: number;
  language: string;
}

export interface Library {
  libraryId: string;
  name: string;
  description?: string;
  category: string;
  tags: string[];
  freshnessScore?: number;
  chunkCount: number;
}
