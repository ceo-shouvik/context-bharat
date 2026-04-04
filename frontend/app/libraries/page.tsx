/**
 * Public library browser — search and filter all indexed libraries.
 * This is the public version (no auth required).
 */
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getLibraries, type Library } from "@/lib/api";
import { LibraryCard } from "@/components/library-card";
import { useLibraryCount, formatLibraryCount } from "@/lib/use-library-count";

const CATEGORIES = [
  { value: "", label: "All" },
  { value: "indian-fintech", label: "Fintech" },
  { value: "india-dpi", label: "India DPI" },
  { value: "indian-trading", label: "Trading" },
  { value: "enterprise-india", label: "Enterprise" },
  { value: "indian-ai", label: "Indian AI" },
  { value: "global-framework", label: "Frameworks" },
  { value: "saas-cloud", label: "SaaS" },
];

export default function PublicLibrariesPage() {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const libraryCount = useLibraryCount();

  useEffect(() => {
    fetchLibraries();
  }, [category]);

  async function fetchLibraries() {
    setLoading(true);
    setError(null);
    try {
      const data = await getLibraries({
        category: category || undefined,
        q: search || undefined,
        limit: 100,
      });
      setLibraries(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load libraries");
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    fetchLibraries();
  }

  const filtered = search
    ? libraries.filter(
        (lib) =>
          lib.name.toLowerCase().includes(search.toLowerCase()) ||
          lib.description?.toLowerCase().includes(search.toLowerCase()) ||
          lib.tags?.some((t) => t.toLowerCase().includes(search.toLowerCase())),
      )
    : libraries;

  return (
    <div className="min-h-screen bg-[#05080f]">
      <title>Libraries — contextBharat</title>

      {/* Public Nav */}
      <nav className="border-b border-white/10 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="font-bold text-lg">
              <span className="text-[#f59e1c]">context</span>
              <span className="text-white">Bharat</span>
            </Link>
            <div className="hidden md:flex gap-4 text-sm">
              <Link href="/libraries" className="text-white font-medium">Libraries</Link>
              <Link href="/docs" className="text-gray-400 hover:text-white transition-colors">Docs</Link>
              <Link href="/pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</Link>
            </div>
          </div>
          <Link
            href="/dashboard"
            className="bg-[#f59e1c] text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#fbbf45] transition-colors"
          >
            Get Free API Key
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-white text-2xl font-semibold mb-2">Library Catalog</h1>
        <p className="text-gray-400 mb-8">
          {formatLibraryCount(libraryCount, "Indian")} APIs, government specs, and global frameworks — all queryable via MCP
        </p>

        {/* Search */}
        <form onSubmit={handleSearch} className="flex gap-3 mb-6">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search libraries (e.g. razorpay, upi, zerodha)"
            className="flex-1 bg-[#0c1120] border border-[#1e2d44] rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#f59e1c]"
          />
          <button
            type="submit"
            className="bg-[#f59e1c] text-black px-6 py-3 rounded-xl text-sm font-medium hover:bg-[#fbbf45] transition-colors"
          >
            Search
          </button>
        </form>

        {/* Category Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {CATEGORIES.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => setCategory(value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                category === value
                  ? "bg-[#f59e1c] text-black"
                  : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Results */}
        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5 animate-pulse"
              >
                <div className="h-4 bg-white/5 rounded w-1/2 mb-3" />
                <div className="h-3 bg-white/5 rounded w-full mb-2" />
                <div className="h-3 bg-white/5 rounded w-3/4" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl p-4">
            {error}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-gray-500 text-center py-16">
            <p className="text-lg mb-2">No libraries indexed yet</p>
            <p className="text-sm">Libraries are being indexed. Check back soon or browse our <Link href="/docs" className="text-[#f59e1c] hover:underline">documentation</Link>.</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((lib) => (
              <LibraryCard key={lib.library_id} library={lib} />
            ))}
          </div>
        )}

        <div className="text-gray-600 text-xs text-center mt-8">
          {filtered.length} {filtered.length === 1 ? "library" : "libraries"} shown
          {category && ` in ${CATEGORIES.find((c) => c.value === category)?.label}`}
        </div>
      </div>
    </div>
  );
}
