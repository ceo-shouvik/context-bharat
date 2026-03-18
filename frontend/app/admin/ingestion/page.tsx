"use client";

import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/admin-api";

interface IngestionRun {
  id: string;
  library_id: string;
  status: "pending" | "running" | "success" | "failed";
  chunks_indexed: number | null;
  duration_seconds: number | null;
  cost_usd: number | null;
  errors: Array<{ message: string; stage: string }>;
  started_at: string;
  completed_at: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-500/10 text-gray-400",
  running: "bg-blue-500/10 text-blue-400",
  success: "bg-green-500/10 text-green-400",
  failed: "bg-red-500/10 text-red-400",
};

export default function AdminIngestion() {
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    loadRuns();
  }, []);

  async function loadRuns() {
    try {
      const data = await adminFetch<{ runs: IngestionRun[] }>("/v1/admin/ingestion/runs");
      setRuns(data.runs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load ingestion runs");
    } finally {
      setLoading(false);
    }
  }

  const filtered = runs.filter((r) => statusFilter === "all" || r.status === statusFilter);

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading ingestion runs...</div>;
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
        <h1 className="text-2xl font-bold text-white">Ingestion Monitor</h1>
        <p className="text-gray-500 text-sm mt-1">Recent ingestion pipeline runs</p>
      </div>

      {/* Status filter */}
      <div className="flex gap-2">
        {["all", "success", "failed", "running", "pending"].map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              statusFilter === s
                ? "bg-[#f59e1c]/10 text-[#f59e1c] border border-[#f59e1c]/30"
                : "bg-[#0c1120] text-gray-400 border border-[#1e2d44] hover:text-white"
            }`}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="border border-[#1e2d44] rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[#0a0f1a] text-gray-400 text-xs uppercase tracking-wider">
              <th className="text-left px-4 py-3">Library</th>
              <th className="text-center px-4 py-3">Status</th>
              <th className="text-right px-4 py-3">Chunks</th>
              <th className="text-right px-4 py-3">Duration</th>
              <th className="text-right px-4 py-3">Cost</th>
              <th className="text-right px-4 py-3">Errors</th>
              <th className="text-left px-4 py-3">Started</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((run) => (
              <>
                <tr
                  key={run.id}
                  onClick={() => setExpandedId(expandedId === run.id ? null : run.id)}
                  className="border-t border-[#1e2d44] bg-[#0c1120] hover:bg-[#0e1528] transition-colors cursor-pointer"
                >
                  <td className="px-4 py-3 text-white">{run.library_id}</td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[run.status] ?? ""}`}
                    >
                      {run.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right text-gray-300">
                    {run.chunks_indexed != null ? run.chunks_indexed.toLocaleString() : "-"}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-400">
                    {run.duration_seconds != null ? `${run.duration_seconds.toFixed(1)}s` : "-"}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-400">
                    {run.cost_usd != null ? `$${run.cost_usd.toFixed(4)}` : "-"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {run.errors.length > 0 ? (
                      <span className="text-red-400">{run.errors.length}</span>
                    ) : (
                      <span className="text-gray-600">0</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">
                    {new Date(run.started_at).toLocaleString()}
                  </td>
                </tr>
                {expandedId === run.id && run.errors.length > 0 && (
                  <tr key={`${run.id}-detail`} className="bg-[#080d18]">
                    <td colSpan={7} className="px-4 py-3">
                      <div className="space-y-2">
                        <p className="text-xs text-gray-500 uppercase tracking-wider">Error Details</p>
                        {run.errors.map((err, i) => (
                          <div
                            key={i}
                            className="bg-red-500/5 border border-red-500/20 rounded p-3 text-sm"
                          >
                            <p className="text-red-300">{err.message}</p>
                            <p className="text-red-500/60 text-xs mt-1">Stage: {err.stage}</p>
                          </div>
                        ))}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-8 text-gray-500 text-sm">No ingestion runs found.</div>
        )}
      </div>
    </div>
  );
}
