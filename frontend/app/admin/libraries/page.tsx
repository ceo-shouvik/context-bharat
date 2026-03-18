"use client";

import { useEffect, useState, useCallback } from "react";
import { adminFetch } from "@/lib/admin-api";

interface AdminLibrary {
  id: string;
  library_id: string;
  name: string;
  category: string;
  chunk_count: number;
  freshness_score: number;
  is_active: boolean;
  last_indexed_at: string | null;
}

export default function AdminLibraries() {
  const [libraries, setLibraries] = useState<AdminLibrary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [togglingId, setTogglingId] = useState<string | null>(null);
  const [reindexingId, setReindexingId] = useState<string | null>(null);

  const loadLibraries = useCallback(async () => {
    try {
      const data = await adminFetch<{ libraries: AdminLibrary[] }>("/v1/admin/libraries");
      setLibraries(data.libraries);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load libraries");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLibraries();
  }, [loadLibraries]);

  async function toggleLibrary(lib: AdminLibrary) {
    setTogglingId(lib.id);
    try {
      await adminFetch(`/v1/admin/libraries/${lib.id}/toggle`, { method: "POST" });
      setLibraries((prev) =>
        prev.map((l) => (l.id === lib.id ? { ...l, is_active: !l.is_active } : l)),
      );
    } catch {
      // Silently fail — the UI will remain unchanged
    } finally {
      setTogglingId(null);
    }
  }

  async function reindexLibrary(lib: AdminLibrary) {
    setReindexingId(lib.id);
    try {
      await adminFetch(`/v1/admin/libraries/${lib.id}/reindex`, { method: "POST" });
    } catch {
      // Silently fail
    } finally {
      setReindexingId(null);
    }
  }

  const categories = Array.from(new Set(libraries.map((l) => l.category))).sort();

  const filtered = libraries.filter((lib) => {
    const matchesSearch =
      !search ||
      lib.name.toLowerCase().includes(search.toLowerCase()) ||
      lib.library_id.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === "all" || lib.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading libraries...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Library Management</h1>
        <p className="text-gray-500 text-sm mt-1">{libraries.length} libraries total</p>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or ID..."
          className="flex-1 max-w-sm px-3 py-2 bg-[#0c1120] border border-[#1e2d44] rounded-md text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#f59e1c]"
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2 bg-[#0c1120] border border-[#1e2d44] rounded-md text-white text-sm focus:outline-none focus:border-[#f59e1c]"
        >
          <option value="all">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="border border-[#1e2d44] rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[#0a0f1a] text-gray-400 text-xs uppercase tracking-wider">
              <th className="text-left px-4 py-3">Name</th>
              <th className="text-left px-4 py-3">Category</th>
              <th className="text-right px-4 py-3">Chunks</th>
              <th className="text-right px-4 py-3">Freshness</th>
              <th className="text-center px-4 py-3">Status</th>
              <th className="text-left px-4 py-3">Last Indexed</th>
              <th className="text-right px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((lib) => (
              <tr
                key={lib.id}
                className="border-t border-[#1e2d44] bg-[#0c1120] hover:bg-[#0e1528] transition-colors"
              >
                <td className="px-4 py-3">
                  <p className="text-white font-medium">{lib.name}</p>
                  <p className="text-gray-500 text-xs">{lib.library_id}</p>
                </td>
                <td className="px-4 py-3 text-gray-400">{lib.category}</td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {lib.chunk_count.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={
                      lib.freshness_score > 0.7
                        ? "text-green-400"
                        : lib.freshness_score > 0.4
                          ? "text-yellow-400"
                          : "text-red-400"
                    }
                  >
                    {(lib.freshness_score * 100).toFixed(0)}%
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <button
                    onClick={() => toggleLibrary(lib)}
                    disabled={togglingId === lib.id}
                    className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                      lib.is_active
                        ? "bg-green-500/10 text-green-400 hover:bg-green-500/20"
                        : "bg-red-500/10 text-red-400 hover:bg-red-500/20"
                    } ${togglingId === lib.id ? "opacity-50" : ""}`}
                  >
                    {lib.is_active ? "Active" : "Disabled"}
                  </button>
                </td>
                <td className="px-4 py-3 text-gray-400 text-xs">
                  {lib.last_indexed_at
                    ? new Date(lib.last_indexed_at).toLocaleString()
                    : "Never"}
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => reindexLibrary(lib)}
                    disabled={reindexingId === lib.id}
                    className={`px-3 py-1 bg-[#f59e1c]/10 text-[#f59e1c] rounded text-xs font-medium hover:bg-[#f59e1c]/20 transition-colors ${
                      reindexingId === lib.id ? "opacity-50" : ""
                    }`}
                  >
                    {reindexingId === lib.id ? "Reindexing..." : "Reindex"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-8 text-gray-500 text-sm">No libraries match your filters.</div>
        )}
      </div>
    </div>
  );
}
