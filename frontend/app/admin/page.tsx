"use client";

import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/admin-api";

interface AdminStats {
  total_libraries: number;
  active_libraries: number;
  total_chunks: number;
  api_keys: number;
  failed_runs_24h: number;
  avg_freshness: number;
  health: {
    database: boolean;
    redis: boolean;
    mcp: boolean;
  };
}

interface RecentError {
  id: string;
  library_id: string;
  error_message: string;
  stage: string;
  timestamp: string;
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-5">
      <p className="text-gray-500 text-xs uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color ?? "text-white"}`}>{value}</p>
    </div>
  );
}

function HealthDot({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`w-2.5 h-2.5 rounded-full ${ok ? "bg-green-500" : "bg-red-500"}`}
      />
      <span className="text-sm text-gray-300">{label}</span>
      <span className={`text-xs ${ok ? "text-green-400" : "text-red-400"}`}>
        {ok ? "healthy" : "down"}
      </span>
    </div>
  );
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [errors, setErrors] = useState<RecentError[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [statsData, errorsData] = await Promise.all([
        adminFetch<AdminStats>("/v1/admin/stats"),
        adminFetch<RecentError[]>("/v1/admin/errors/recent"),
      ]);
      setStats(statsData);
      setErrors(errorsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load admin data");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading dashboard...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
        {error}
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">System overview and health status</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard label="Total Libraries" value={stats.total_libraries} />
        <StatCard label="Active Libraries" value={stats.active_libraries} color="text-green-400" />
        <StatCard label="Total Chunks" value={stats.total_chunks.toLocaleString()} />
        <StatCard label="API Keys" value={stats.api_keys} />
        <StatCard
          label="Failed Runs (24h)"
          value={stats.failed_runs_24h}
          color={stats.failed_runs_24h > 0 ? "text-red-400" : "text-green-400"}
        />
        <StatCard
          label="Avg Freshness"
          value={`${(stats.avg_freshness * 100).toFixed(1)}%`}
          color={stats.avg_freshness > 0.7 ? "text-green-400" : "text-yellow-400"}
        />
      </div>

      {/* System Health */}
      <div className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-5">
        <h2 className="text-white font-semibold mb-4">System Health</h2>
        <div className="flex gap-8">
          <HealthDot ok={stats.health.database} label="Database" />
          <HealthDot ok={stats.health.redis} label="Redis" />
          <HealthDot ok={stats.health.mcp} label="MCP Server" />
        </div>
      </div>

      {/* Recent Errors */}
      <div className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-5">
        <h2 className="text-white font-semibold mb-4">Recent Errors</h2>
        {errors.length === 0 ? (
          <p className="text-gray-500 text-sm">No recent errors</p>
        ) : (
          <div className="space-y-3">
            {errors.slice(0, 5).map((err) => (
              <div
                key={err.id}
                className="flex items-start justify-between border-b border-[#1e2d44] pb-3 last:border-0 last:pb-0"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-white truncate">{err.error_message}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {err.library_id} &middot; {err.stage} &middot;{" "}
                    {new Date(err.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
