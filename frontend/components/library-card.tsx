/**
 * LibraryCard — displays a library with freshness, category badge, and language flags.
 */
"use client";

import type { Library } from "@/lib/api";

const CATEGORY_COLORS: Record<string, string> = {
  "indian-fintech":   "bg-amber-500/15 text-amber-400 border-amber-500/25",
  "india-dpi":        "bg-green-500/15 text-green-400 border-green-500/25",
  "indian-trading":   "bg-blue-500/15 text-blue-400 border-blue-500/25",
  "enterprise-india": "bg-purple-500/15 text-purple-400 border-purple-500/25",
  "indian-ai":        "bg-pink-500/15 text-pink-400 border-pink-500/25",
  "global-framework": "bg-slate-500/15 text-slate-400 border-slate-500/25",
  "saas-cloud":       "bg-cyan-500/15 text-cyan-400 border-cyan-500/25",
};

const CATEGORY_LABELS: Record<string, string> = {
  "indian-fintech":   "Fintech",
  "india-dpi":        "India DPI",
  "indian-trading":   "Trading",
  "enterprise-india": "Enterprise",
  "indian-ai":        "Indian AI",
  "global-framework": "Framework",
  "saas-cloud":       "SaaS",
};

interface Props {
  library: Library;
  onClick?: () => void;
}

export function LibraryCard({ library, onClick }: Props) {
  const freshnessPercent = Math.round((library.freshness_score ?? 0) * 100);
  const colorClass = CATEGORY_COLORS[library.category] ?? CATEGORY_COLORS["global-framework"];
  const categoryLabel = CATEGORY_LABELS[library.category] ?? library.category;

  return (
    <div
      onClick={onClick}
      className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5 cursor-pointer hover:border-[#253650] transition-all"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="font-semibold text-white text-sm">{library.name}</div>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${colorClass}`}>
          {categoryLabel}
        </span>
      </div>

      {/* Description */}
      {library.description && (
        <p className="text-gray-400 text-xs leading-relaxed mb-3 line-clamp-2">
          {library.description}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {library.tags?.slice(0, 2).map((tag) => (
            <span key={tag} className="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded">
              {tag}
            </span>
          ))}
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <FreshnessIndicator score={library.freshness_score} />
          <span>{library.chunk_count.toLocaleString()} chunks</span>
        </div>
      </div>
    </div>
  );
}

function FreshnessIndicator({ score }: { score?: number }) {
  if (score === undefined) return null;
  const color = score > 0.8 ? "bg-green-400" : score > 0.5 ? "bg-amber-400" : "bg-red-400";
  const label = score > 0.8 ? "Fresh" : score > 0.5 ? "Aging" : "Stale";
  return (
    <span className="flex items-center gap-1">
      <span className={`w-1.5 h-1.5 rounded-full ${color}`} />
      <span>{label}</span>
    </span>
  );
}
