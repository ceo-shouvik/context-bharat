/**
 * QueryTester — interactive doc query sandbox.
 * Lets developers test any library + query directly in the browser.
 */
"use client";

import { useState } from "react";
import { queryDocs } from "@/lib/api";

interface Props {
  defaultLibraryId?: string;
  apiKey?: string;
}

export function QueryTester({ defaultLibraryId = "", apiKey }: Props) {
  const [libraryId, setLibraryId] = useState(defaultLibraryId);
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("en");
  const [result, setResult] = useState<string | null>(null);
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleQuery() {
    if (!libraryId.trim() || !query.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await queryDocs({ libraryId, query, language, apiKey });
      setResult(data.docs);
      setSources(data.sources);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden">
      {/* Input area */}
      <div className="p-4 border-b border-[#1e2d44]">
        <div className="flex gap-2 mb-3">
          <input
            value={libraryId}
            onChange={(e) => setLibraryId(e.target.value)}
            placeholder="/razorpay/razorpay-sdk"
            className="flex-1 bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#f59e1c]"
          />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#f59e1c]"
          >
            <option value="en">English</option>
            <option value="hi">हिंदी</option>
            <option value="ta">தமிழ்</option>
            <option value="te">తెలుగు</option>
          </select>
        </div>
        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
            placeholder="How do I create a payment link with expiry?"
            className="flex-1 bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#f59e1c]"
          />
          <button
            onClick={handleQuery}
            disabled={loading || !libraryId || !query}
            className="bg-[#f59e1c] text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#fbbf45] disabled:opacity-50 transition-colors whitespace-nowrap"
          >
            {loading ? "..." : "Query"}
          </button>
        </div>
      </div>

      {/* Result area */}
      <div className="p-4 min-h-[200px]">
        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <span className="animate-spin">⟳</span> Fetching docs...
          </div>
        )}
        {error && (
          <div className="text-red-400 text-sm bg-red-500/10 p-3 rounded-lg">{error}</div>
        )}
        {result && (
          <div>
            <pre className="text-gray-300 text-xs leading-relaxed whitespace-pre-wrap font-mono overflow-auto max-h-96">
              {result}
            </pre>
            {sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-[#1e2d44]">
                <div className="text-xs text-gray-500">Sources:</div>
                <div className="flex flex-wrap gap-2 mt-1">
                  {sources.map((src) => (
                    <a
                      key={src}
                      href={src}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-[#f59e1c] hover:underline truncate max-w-xs"
                    >
                      {src}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        {!loading && !error && !result && (
          <div className="text-gray-600 text-sm text-center mt-8">
            Enter a library ID and query to test
          </div>
        )}
      </div>
    </div>
  );
}
