/**
 * UsageChart — displays query usage over the last 7 days using Recharts.
 */
"use client";

import { useEffect, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface DailyUsage {
  date: string;
  queries: number;
}

function generatePlaceholderData(): DailyUsage[] {
  const data: DailyUsage[] = [];
  const now = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    data.push({
      date: d.toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
      queries: Math.floor(Math.random() * 80) + 5,
    });
  }
  return data;
}

export function UsageChart() {
  const [data, setData] = useState<DailyUsage[]>([]);
  const [totalToday, setTotalToday] = useState(0);
  const [totalMonth, setTotalMonth] = useState(0);

  useEffect(() => {
    // TODO: Fetch real usage data from API when available
    const placeholder = generatePlaceholderData();
    setData(placeholder);
    setTotalToday(placeholder[placeholder.length - 1]?.queries ?? 0);
    setTotalMonth(placeholder.reduce((sum, d) => sum + d.queries, 0));
  }, []);

  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
      {/* Stats */}
      <div className="flex gap-8 mb-6">
        <div>
          <div className="text-2xl font-bold text-white">{totalToday}</div>
          <div className="text-xs text-gray-500">Queries today</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white">{totalMonth}</div>
          <div className="text-xs text-gray-500">This week</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-green-400">Active</div>
          <div className="text-xs text-gray-500">MCP status</div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="queryGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e1c" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#f59e1c" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#6b7280", fontSize: 11 }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#6b7280", fontSize: 11 }}
              width={30}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0c1120",
                border: "1px solid #1e2d44",
                borderRadius: "8px",
                color: "#fff",
                fontSize: "12px",
              }}
              labelStyle={{ color: "#9ca3af" }}
            />
            <Area
              type="monotone"
              dataKey="queries"
              stroke="#f59e1c"
              strokeWidth={2}
              fill="url(#queryGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
