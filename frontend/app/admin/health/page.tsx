"use client";

import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/admin-api";

interface HealthDetailed {
  database: {
    healthy: boolean;
    version: string;
    table_counts: Record<string, number>;
    connection_pool: number;
  };
  redis: {
    healthy: boolean;
    memory_used_mb: number;
    total_keys: number;
    connected_clients: number;
  };
  feature_flags: {
    total: number;
    enabled: number;
    disabled: number;
  };
  mcp_server: {
    healthy: boolean;
    url: string;
    response_time_ms: number;
  };
}

function StatusIndicator({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-block w-3 h-3 rounded-full ${ok ? "bg-green-500" : "bg-red-500"}`}
    />
  );
}

function HealthCard({
  title,
  healthy,
  children,
}: {
  title: string;
  healthy: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-5">
      <div className="flex items-center gap-3 mb-4">
        <StatusIndicator ok={healthy} />
        <h2 className="text-white font-semibold">{title}</h2>
        <span
          className={`text-xs ml-auto ${healthy ? "text-green-400" : "text-red-400"}`}
        >
          {healthy ? "Healthy" : "Unhealthy"}
        </span>
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="text-gray-300 font-mono text-xs">{value}</span>
    </div>
  );
}

export default function AdminHealth() {
  const [health, setHealth] = useState<HealthDetailed | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadHealth();
  }, []);

  async function loadHealth() {
    try {
      const data = await adminFetch<HealthDetailed>("/v1/admin/health/detailed");
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load health data");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading health status...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
        {error}
      </div>
    );
  }

  if (!health) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Health</h1>
          <p className="text-gray-500 text-sm mt-1">Detailed service status</p>
        </div>
        <button
          onClick={() => {
            setLoading(true);
            loadHealth();
          }}
          className="px-3 py-1.5 bg-[#0c1120] border border-[#1e2d44] rounded-md text-sm text-gray-400 hover:text-white transition-colors"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Database */}
        <HealthCard title="Database (PostgreSQL)" healthy={health.database.healthy}>
          <DetailRow label="Version" value={health.database.version} />
          <DetailRow label="Connection Pool" value={health.database.connection_pool} />
          <div className="pt-2 mt-2 border-t border-[#1e2d44]">
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Table Counts</p>
            {Object.entries(health.database.table_counts).map(([table, count]) => (
              <DetailRow key={table} label={table} value={count.toLocaleString()} />
            ))}
          </div>
        </HealthCard>

        {/* Redis */}
        <HealthCard title="Redis" healthy={health.redis.healthy}>
          <DetailRow label="Memory Used" value={`${health.redis.memory_used_mb.toFixed(1)} MB`} />
          <DetailRow label="Total Keys" value={health.redis.total_keys.toLocaleString()} />
          <DetailRow label="Connected Clients" value={health.redis.connected_clients} />
        </HealthCard>

        {/* Feature Flags */}
        <HealthCard title="Feature Flags" healthy={true}>
          <DetailRow label="Total Flags" value={health.feature_flags.total} />
          <DetailRow label="Enabled" value={health.feature_flags.enabled} />
          <DetailRow label="Disabled" value={health.feature_flags.disabled} />
        </HealthCard>

        {/* MCP Server */}
        <HealthCard title="MCP Server" healthy={health.mcp_server.healthy}>
          <DetailRow label="URL" value={health.mcp_server.url} />
          <DetailRow
            label="Response Time"
            value={`${health.mcp_server.response_time_ms} ms`}
          />
        </HealthCard>
      </div>
    </div>
  );
}
