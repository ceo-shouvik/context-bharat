/**
 * Library detail page — individual library info + query playground.
 */
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getLibraries, queryDocs, type Library } from "@/lib/api";

export default function LibraryDetailPage() {
  const params = useParams();
  const libraryId = decodeURIComponent(params.id as string);

  const [library, setLibrary] = useState<Library | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("en");
  const [result, setResult] = useState<string | null>(null);
  const [sources, setSources] = useState<string[]>([]);
  const [querying, setQuerying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLibrary();
  }, [libraryId]);

  async function fetchLibrary() {
    try {
      const libs = await getLibraries({ limit: 200 });
      const found = libs.find(
        (l) => l.library_id === libraryId || l.library_id === `/${libraryId}`,
      );
      setLibrary(found ?? null);
    } catch {
      setError("Failed to load library");
    } finally {
      setLoading(false);
    }
  }

  async function handleQuery() {
    if (!query.trim() || !library) return;
    setQuerying(true);
    setError(null);
    setResult(null);
    try {
      const data = await queryDocs({
        libraryId: library.library_id,
        query,
        language,
      });
      setResult(data.docs);
      setSources(data.sources);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setQuerying(false);
    }
  }

  const CATEGORY_COLORS: Record<string, string> = {
    "indian-fintech": "bg-amber-500/15 text-amber-400 border-amber-500/25",
    "india-dpi": "bg-green-500/15 text-green-400 border-green-500/25",
    "indian-trading": "bg-blue-500/15 text-blue-400 border-blue-500/25",
    "enterprise-india": "bg-purple-500/15 text-purple-400 border-purple-500/25",
    "indian-ai": "bg-pink-500/15 text-pink-400 border-pink-500/25",
    "global-framework": "bg-slate-500/15 text-slate-400 border-slate-500/25",
    "saas-cloud": "bg-cyan-500/15 text-cyan-400 border-cyan-500/25",
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05080f] flex items-center justify-center">
        <div className="text-gray-400 text-sm">Loading library...</div>
      </div>
    );
  }

  if (!library) {
    return (
      <div className="min-h-screen bg-[#05080f] flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-4">Library not found</div>
          <Link href="/libraries" className="text-[#f59e1c] text-sm hover:underline">
            Browse all libraries
          </Link>
        </div>
      </div>
    );
  }

  const colorClass =
    CATEGORY_COLORS[library.category] ?? CATEGORY_COLORS["global-framework"];
  const freshnessPercent = Math.round((library.freshness_score ?? 0) * 100);

  return (
    <div className="min-h-screen bg-[#05080f]">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Breadcrumb */}
        <div className="text-sm text-gray-500 mb-6">
          <Link href="/libraries" className="hover:text-white transition-colors">
            Libraries
          </Link>
          <span className="mx-2">/</span>
          <span className="text-white">{library.name}</span>
        </div>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-3">
            <h1 className="text-3xl font-bold text-white">{library.name}</h1>
            <span
              className={`text-xs font-semibold px-3 py-1 rounded border ${colorClass}`}
            >
              {library.category}
            </span>
          </div>
          {library.description && (
            <p className="text-gray-400 text-lg mb-4">{library.description}</p>
          )}
          <div className="flex flex-wrap gap-2 mb-4">
            {library.tags?.map((tag) => (
              <span
                key={tag}
                className="text-xs text-gray-400 bg-white/5 px-3 py-1 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            <div>
              <span className="text-white font-medium">{library.chunk_count.toLocaleString()}</span>{" "}
              chunks indexed
            </div>
            <div>
              Freshness:{" "}
              <span
                className={
                  freshnessPercent > 80
                    ? "text-green-400"
                    : freshnessPercent > 50
                      ? "text-amber-400"
                      : "text-red-400"
                }
              >
                {freshnessPercent}%
              </span>
            </div>
            <div>
              ID:{" "}
              <code className="text-gray-400 font-mono text-xs">{library.library_id}</code>
            </div>
          </div>
        </div>

        {/* MCP Usage */}
        <section className="mb-8">
          <h2 className="text-white font-semibold mb-3">Use with MCP</h2>
          <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
            <p className="text-gray-400 text-sm mb-3">
              Just mention this library in your prompt:
            </p>
            <pre className="bg-black/40 rounded-lg p-4 text-sm font-mono overflow-x-auto">
              <span className="text-gray-400">How do I integrate {library.name}?</span>{" "}
              <span className="text-[#f59e1c]">use contextbharat</span>
            </pre>
            <p className="text-gray-500 text-xs mt-3">
              The MCP server will automatically resolve{" "}
              <code className="text-gray-400">{library.library_id}</code> and fetch relevant docs.
            </p>
          </div>
        </section>

        {/* Query Playground */}
        <section className="mb-8">
          <h2 className="text-white font-semibold mb-3">Query Playground</h2>
          <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden">
            <div className="p-4 border-b border-[#1e2d44]">
              <div className="flex gap-2">
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleQuery()}
                  placeholder={`Ask about ${library.name}...`}
                  className="flex-1 bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#f59e1c]"
                />
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2 text-sm text-white"
                >
                  <option value="en">English</option>
                  <option value="hi">Hindi</option>
                  <option value="ta">Tamil</option>
                  <option value="te">Telugu</option>
                </select>
                <button
                  onClick={handleQuery}
                  disabled={querying || !query}
                  className="bg-[#f59e1c] text-black px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-[#fbbf45] disabled:opacity-50 transition-colors"
                >
                  {querying ? "..." : "Query"}
                </button>
              </div>
            </div>
            <div className="p-4 min-h-[250px]">
              {querying && (
                <div className="flex items-center gap-2 text-gray-400 text-sm">
                  <span className="animate-spin">&#10227;</span> Fetching docs...
                </div>
              )}
              {error && (
                <div className="text-red-400 text-sm bg-red-500/10 p-3 rounded-lg">{error}</div>
              )}
              {result && (
                <div>
                  <pre className="text-gray-300 text-xs leading-relaxed whitespace-pre-wrap font-mono overflow-auto max-h-[500px]">
                    {result}
                  </pre>
                  {sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-[#1e2d44]">
                      <div className="text-xs text-gray-500 mb-1">Sources:</div>
                      <div className="flex flex-wrap gap-2">
                        {sources.map((src) => (
                          <a
                            key={src}
                            href={src}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-[#f59e1c] hover:underline truncate max-w-sm"
                          >
                            {src}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {!querying && !error && !result && (
                <div className="text-gray-600 text-sm text-center mt-16">
                  Ask anything about {library.name} — authentication, API endpoints, webhooks, SDKs...
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
