"use client";

import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/admin-api";

interface FeatureFlag {
  name: string;
  description: string;
  enabled: boolean;
}

export default function AdminFlags() {
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [togglingFlag, setTogglingFlag] = useState<string | null>(null);

  useEffect(() => {
    loadFlags();
  }, []);

  async function loadFlags() {
    try {
      const data = await adminFetch<{ flags: FeatureFlag[] }>("/v1/admin/flags");
      setFlags(data.flags);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load flags");
    } finally {
      setLoading(false);
    }
  }

  async function toggleFlag(flagName: string) {
    setTogglingFlag(flagName);
    try {
      const flag = flags.find((f) => f.name === flagName);
      await adminFetch(`/v1/admin/flags/${flagName}`, {
        method: "POST",
        body: JSON.stringify({ enabled: !flag?.enabled }),
      });
      setFlags((prev) =>
        prev.map((f) => (f.name === flagName ? { ...f, enabled: !f.enabled } : f)),
      );
    } catch {
      // Silently fail
    } finally {
      setTogglingFlag(null);
    }
  }

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading feature flags...</div>;
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
        <h1 className="text-2xl font-bold text-white">Feature Flags</h1>
        <p className="text-gray-500 text-sm mt-1">Toggle feature flags in real-time</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {flags.map((flag) => (
          <div
            key={flag.name}
            className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-4 flex items-center justify-between"
          >
            <div className="min-w-0 flex-1 mr-4">
              <p className="text-sm font-medium text-white">{flag.name}</p>
              <p className="text-xs text-gray-500 mt-0.5">{flag.description}</p>
            </div>
            <button
              onClick={() => toggleFlag(flag.name)}
              disabled={togglingFlag === flag.name}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0 ${
                flag.enabled ? "bg-green-500" : "bg-red-500/40"
              } ${togglingFlag === flag.name ? "opacity-50" : ""}`}
            >
              <span
                className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                  flag.enabled ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        ))}
      </div>

      {flags.length === 0 && (
        <div className="text-center py-8 text-gray-500 text-sm">No feature flags configured.</div>
      )}
    </div>
  );
}
