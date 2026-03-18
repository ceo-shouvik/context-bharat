/**
 * ApiKeyManager — create, view, and revoke API keys.
 */
"use client";

import { useEffect, useState } from "react";

interface ApiKey {
  id: string;
  key_prefix: string;
  name: string | null;
  tier: string;
  daily_limit: number;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
}

interface NewKey {
  key: string;
  key_prefix: string;
  tier: string;
  daily_limit: number;
}

export function ApiKeyManager() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [newKey, setNewKey] = useState<NewKey | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [keyName, setKeyName] = useState("");

  useEffect(() => { fetchKeys(); }, []);

  async function fetchKeys() {
    try {
      const res = await fetch("/api/keys");
      if (res.ok) setKeys(await res.json());
    } finally {
      setLoading(false);
    }
  }

  async function createKey() {
    setCreating(true);
    try {
      const res = await fetch("/api/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: keyName || undefined }),
      });
      if (res.ok) {
        const data = await res.json();
        setNewKey(data);
        setKeyName("");
        fetchKeys();
      }
    } finally {
      setCreating(false);
    }
  }

  async function revokeKey(keyId: string) {
    if (!confirm("Revoke this API key? This cannot be undone.")) return;
    await fetch(`/api/keys?id=${keyId}`, { method: "DELETE" });
    fetchKeys();
  }

  return (
    <div>
      {/* New key revealed */}
      {newKey && (
        <div className="bg-green-500/10 border border-green-500/25 rounded-xl p-4 mb-6">
          <div className="text-green-400 font-semibold text-sm mb-2">
            ✓ API key created — copy it now, it won&apos;t be shown again
          </div>
          <code className="block bg-black/30 rounded-lg p-3 text-green-300 text-sm font-mono break-all">
            {newKey.key}
          </code>
          <button
            onClick={() => { navigator.clipboard.writeText(newKey.key); }}
            className="mt-2 text-xs text-green-400 hover:text-green-300"
          >
            Copy to clipboard
          </button>
        </div>
      )}

      {/* Create new key */}
      <div className="flex gap-3 mb-6">
        <input
          value={keyName}
          onChange={(e) => setKeyName(e.target.value)}
          placeholder="Key name (optional)"
          className="flex-1 bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#f59e1c]"
        />
        <button
          onClick={createKey}
          disabled={creating}
          className="bg-[#f59e1c] text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#fbbf45] disabled:opacity-50 transition-colors"
        >
          {creating ? "Creating..." : "+ New Key"}
        </button>
      </div>

      {/* Key list */}
      {loading ? (
        <div className="text-gray-500 text-sm">Loading keys...</div>
      ) : keys.length === 0 ? (
        <div className="text-gray-500 text-sm text-center py-8">
          No API keys yet. Create one above.
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {keys.map((key) => (
            <div
              key={key.id}
              className="flex items-center justify-between bg-[#131e30] border border-[#1e2d44] rounded-xl px-4 py-3"
            >
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <code className="text-sm font-mono text-gray-300">{key.key_prefix}...</code>
                  {key.name && <span className="text-xs text-gray-500">{key.name}</span>}
                  <span className={`text-xs px-2 py-0.5 rounded border ${
                    key.tier === "pro"
                      ? "bg-[#f59e1c]/15 text-[#f59e1c] border-[#f59e1c]/25"
                      : "bg-gray-500/15 text-gray-400 border-gray-500/25"
                  }`}>
                    {key.tier}
                  </span>
                </div>
                <div className="text-xs text-gray-600">
                  {key.daily_limit} queries/day ·{" "}
                  {key.last_used_at
                    ? `Last used ${new Date(key.last_used_at).toLocaleDateString()}`
                    : "Never used"}
                </div>
              </div>
              <button
                onClick={() => revokeKey(key.id)}
                className="text-xs text-red-400 hover:text-red-300 transition-colors"
              >
                Revoke
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
