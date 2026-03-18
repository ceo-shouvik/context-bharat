"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { adminFetch } from "@/lib/admin-api";

interface QueryVolumePoint {
  date: string;
  queries: number;
}

interface PopularLibrary {
  library_id: string;
  queries: number;
}

interface LanguageBreakdown {
  language: string;
  count: number;
}

const PIE_COLORS = [
  "#f59e1c",
  "#3b82f6",
  "#10b981",
  "#ef4444",
  "#8b5cf6",
  "#ec4899",
  "#f97316",
  "#06b6d4",
];

export default function AdminAnalytics() {
  const [queryVolume, setQueryVolume] = useState<QueryVolumePoint[]>([]);
  const [popularLibs, setPopularLibs] = useState<PopularLibrary[]>([]);
  const [langBreakdown, setLangBreakdown] = useState<LanguageBreakdown[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function loadAnalytics() {
    try {
      const [volume, libs, langs] = await Promise.all([
        adminFetch<{ data: QueryVolumePoint[] }>("/v1/admin/analytics/query-volume"),
        adminFetch<{ data: PopularLibrary[] }>("/v1/admin/analytics/popular-libraries"),
        adminFetch<{ data: LanguageBreakdown[] }>("/v1/admin/analytics/language-breakdown"),
      ]);
      setQueryVolume(volume.data);
      setPopularLibs(libs.data);
      setLangBreakdown(langs.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading analytics...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-gray-500 text-sm mt-1">Usage metrics and trends</p>
      </div>

      {/* Query Volume - Line Chart */}
      <div className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-5">
        <h2 className="text-white font-semibold mb-4">Query Volume (Last 30 Days)</h2>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={queryVolume}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d44" />
              <XAxis
                dataKey="date"
                stroke="#4b5563"
                tick={{ fill: "#6b7280", fontSize: 11 }}
                tickFormatter={(v) => {
                  const d = new Date(v);
                  return `${d.getMonth() + 1}/${d.getDate()}`;
                }}
              />
              <YAxis stroke="#4b5563" tick={{ fill: "#6b7280", fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0a0f1a",
                  border: "1px solid #1e2d44",
                  borderRadius: "6px",
                  color: "#fff",
                  fontSize: "12px",
                }}
              />
              <Line
                type="monotone"
                dataKey="queries"
                stroke="#f59e1c"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: "#f59e1c" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Popular Libraries - Bar Chart */}
        <div className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-5">
          <h2 className="text-white font-semibold mb-4">Popular Libraries (Top 10)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={popularLibs.slice(0, 10)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2d44" />
                <XAxis type="number" stroke="#4b5563" tick={{ fill: "#6b7280", fontSize: 11 }} />
                <YAxis
                  dataKey="library_id"
                  type="category"
                  stroke="#4b5563"
                  tick={{ fill: "#6b7280", fontSize: 10 }}
                  width={120}
                  tickFormatter={(v: string) => v.split("/").pop() ?? v}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0a0f1a",
                    border: "1px solid #1e2d44",
                    borderRadius: "6px",
                    color: "#fff",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="queries" fill="#f59e1c" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Language Breakdown - Pie Chart */}
        <div className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-5">
          <h2 className="text-white font-semibold mb-4">Language Breakdown</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={langBreakdown}
                  dataKey="count"
                  nameKey="language"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                >
                  {langBreakdown.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0a0f1a",
                    border: "1px solid #1e2d44",
                    borderRadius: "6px",
                    color: "#fff",
                    fontSize: "12px",
                  }}
                />
                <Legend
                  wrapperStyle={{ fontSize: "12px", color: "#9ca3af" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
