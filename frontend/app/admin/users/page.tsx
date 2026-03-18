"use client";

import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/admin-api";

interface AdminUser {
  id: string;
  user_id: string;
  key_prefix: string;
  tier: string;
  daily_limit: number;
  last_used_at: string | null;
  is_active: boolean;
}

const TIERS = ["free", "pro", "team"];

export default function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [actionId, setActionId] = useState<string | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    try {
      const data = await adminFetch<{ users: AdminUser[] }>("/v1/admin/users");
      setUsers(data.users);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  }

  async function revokeKey(userId: string) {
    setActionId(userId);
    try {
      await adminFetch(`/v1/admin/users/${userId}/revoke`, { method: "POST" });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, is_active: false } : u)),
      );
    } catch {
      // Silently fail
    } finally {
      setActionId(null);
    }
  }

  async function changeTier(userId: string, newTier: string) {
    setActionId(userId);
    try {
      await adminFetch(`/v1/admin/users/${userId}/tier`, {
        method: "POST",
        body: JSON.stringify({ tier: newTier }),
      });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, tier: newTier } : u)),
      );
    } catch {
      // Silently fail
    } finally {
      setActionId(null);
    }
  }

  const filtered = users.filter((u) => {
    if (!search) return true;
    return u.key_prefix.toLowerCase().includes(search.toLowerCase());
  });

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading users...</div>;
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
        <h1 className="text-2xl font-bold text-white">User &amp; Key Management</h1>
        <p className="text-gray-500 text-sm mt-1">{users.length} API keys total</p>
      </div>

      {/* Search */}
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search by key prefix..."
        className="max-w-sm px-3 py-2 bg-[#0c1120] border border-[#1e2d44] rounded-md text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#f59e1c]"
      />

      {/* Table */}
      <div className="border border-[#1e2d44] rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[#0a0f1a] text-gray-400 text-xs uppercase tracking-wider">
              <th className="text-left px-4 py-3">User ID</th>
              <th className="text-left px-4 py-3">Key Prefix</th>
              <th className="text-center px-4 py-3">Tier</th>
              <th className="text-right px-4 py-3">Daily Limit</th>
              <th className="text-left px-4 py-3">Last Used</th>
              <th className="text-center px-4 py-3">Status</th>
              <th className="text-right px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((user) => (
              <tr
                key={user.id}
                className="border-t border-[#1e2d44] bg-[#0c1120] hover:bg-[#0e1528] transition-colors"
              >
                <td className="px-4 py-3 text-gray-300 text-xs font-mono">
                  {user.user_id.slice(0, 12)}...
                </td>
                <td className="px-4 py-3 text-white font-mono text-xs">{user.key_prefix}...</td>
                <td className="px-4 py-3 text-center">
                  <select
                    value={user.tier}
                    onChange={(e) => changeTier(user.id, e.target.value)}
                    disabled={actionId === user.id || !user.is_active}
                    className="bg-[#0a0f1a] border border-[#1e2d44] rounded text-xs text-white px-2 py-1 focus:outline-none focus:border-[#f59e1c]"
                  >
                    {TIERS.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3 text-right text-gray-400">{user.daily_limit}</td>
                <td className="px-4 py-3 text-gray-400 text-xs">
                  {user.last_used_at
                    ? new Date(user.last_used_at).toLocaleString()
                    : "Never"}
                </td>
                <td className="px-4 py-3 text-center">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      user.is_active
                        ? "bg-green-500/10 text-green-400"
                        : "bg-red-500/10 text-red-400"
                    }`}
                  >
                    {user.is_active ? "Active" : "Revoked"}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  {user.is_active && (
                    <button
                      onClick={() => revokeKey(user.id)}
                      disabled={actionId === user.id}
                      className={`px-3 py-1 bg-red-500/10 text-red-400 rounded text-xs font-medium hover:bg-red-500/20 transition-colors ${
                        actionId === user.id ? "opacity-50" : ""
                      }`}
                    >
                      Revoke
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-8 text-gray-500 text-sm">No users found.</div>
        )}
      </div>
    </div>
  );
}
