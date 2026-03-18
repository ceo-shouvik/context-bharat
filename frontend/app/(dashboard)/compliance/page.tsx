/**
 * Compliance Guide — regulatory requirements and checklists per library.
 */
"use client";

import { useEffect, useState } from "react";
import { features } from "@/lib/features";
import { getLibraries, type Library } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.contextbharat.com";

interface ComplianceItem {
  id: string;
  requirement: string;
  description: string;
  severity: "mandatory" | "recommended" | "best_practice";
  checked?: boolean;
}

interface ComplianceData {
  library_id: string;
  library_name: string;
  regulatory_requirements: string[];
  mandatory_fields: string[];
  checklist: ComplianceItem[];
}

const severityStyles: Record<string, { bg: string; text: string; border: string; label: string }> = {
  mandatory: {
    bg: "bg-red-500/10",
    text: "text-red-400",
    border: "border-red-500/30",
    label: "Mandatory",
  },
  recommended: {
    bg: "bg-yellow-500/10",
    text: "text-yellow-400",
    border: "border-yellow-500/30",
    label: "Recommended",
  },
  best_practice: {
    bg: "bg-green-500/10",
    text: "text-green-400",
    border: "border-green-500/30",
    label: "Best Practice",
  },
};

function ComingSoon() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">&#128220;</div>
        <h2 className="text-white text-xl font-semibold mb-2">
          Compliance Guide — Coming Soon
        </h2>
        <p className="text-gray-400 text-sm max-w-md">
          Regulatory requirements, mandatory fields, and compliance checklists
          for Indian fintech and government API integrations.
        </p>
      </div>
    </div>
  );
}

export default function CompliancePage() {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [selectedLibrary, setSelectedLibrary] = useState("");
  const [data, setData] = useState<ComplianceData | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingLibs, setLoadingLibs] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    async function loadLibraries() {
      try {
        const libs = await getLibraries();
        setLibraries(libs);
      } catch {
        // Non-critical
      } finally {
        setLoadingLibs(false);
      }
    }
    loadLibraries();
  }, []);

  useEffect(() => {
    if (!selectedLibrary || !features.complianceLayer) return;

    async function fetchCompliance() {
      setLoading(true);
      setError(null);
      setData(null);
      setCheckedItems(new Set());
      try {
        const res = await fetch(
          `${API_BASE}/v1/compliance?library_id=${encodeURIComponent(selectedLibrary)}`,
        );
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load compliance data");
      } finally {
        setLoading(false);
      }
    }

    fetchCompliance();
  }, [selectedLibrary]);

  function toggleCheck(id: string) {
    setCheckedItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  if (!features.complianceLayer) {
    return (
      <div className="min-h-screen bg-[#05080f]">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <ComingSoon />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05080f]">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-10">
          <h1 className="text-white text-2xl font-semibold">Compliance Guide</h1>
          <p className="text-gray-400 text-sm mt-1">
            Regulatory requirements and integration checklists for Indian APIs
          </p>
        </div>

        {/* Library selector */}
        <div className="mb-8 max-w-sm">
          <label className="block text-gray-400 text-sm mb-2">Select Library</label>
          <select
            value={selectedLibrary}
            onChange={(e) => setSelectedLibrary(e.target.value)}
            className="bg-[#0c1120] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 w-full focus:border-[#f59e1c] focus:outline-none"
          >
            <option value="">Choose a library...</option>
            {libraries.map((lib) => (
              <option key={lib.library_id} value={lib.library_id}>
                {lib.name}
              </option>
            ))}
          </select>
          {loadingLibs && <p className="text-gray-500 text-xs mt-1">Loading libraries...</p>}
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-gray-400 text-sm">Loading compliance data...</div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm mb-6">
            {error}
          </div>
        )}

        {data && !loading && (
          <div className="grid gap-6">
            {/* Regulatory Requirements */}
            {data.regulatory_requirements.length > 0 && (
              <section className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
                <h2 className="text-white font-medium mb-3">Regulatory Requirements</h2>
                <ul className="space-y-2">
                  {data.regulatory_requirements.map((req, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                      <span className="text-red-400 mt-0.5">*</span>
                      {req}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Mandatory Fields */}
            {data.mandatory_fields.length > 0 && (
              <section className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
                <h2 className="text-white font-medium mb-3">Mandatory Fields</h2>
                <div className="flex flex-wrap gap-2">
                  {data.mandatory_fields.map((field) => (
                    <span
                      key={field}
                      className="text-xs bg-red-500/10 text-red-400 border border-red-500/30 rounded px-2.5 py-1 font-mono"
                    >
                      {field}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {/* Checklist */}
            {data.checklist.length > 0 && (
              <section className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-white font-medium">Compliance Checklist</h2>
                  <span className="text-gray-500 text-xs">
                    {checkedItems.size}/{data.checklist.length} completed
                  </span>
                </div>
                <div className="space-y-3">
                  {data.checklist.map((item) => {
                    const style = severityStyles[item.severity] ?? severityStyles.best_practice;
                    return (
                      <label
                        key={item.id}
                        className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${style.bg} ${style.border} hover:opacity-90`}
                      >
                        <input
                          type="checkbox"
                          checked={checkedItems.has(item.id)}
                          onChange={() => toggleCheck(item.id)}
                          className="mt-0.5 accent-[#f59e1c]"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className={`text-sm font-medium ${style.text}`}>
                              {item.requirement}
                            </span>
                            <span
                              className={`text-[10px] px-1.5 py-0.5 rounded ${style.bg} ${style.text} border ${style.border}`}
                            >
                              {style.label}
                            </span>
                          </div>
                          <p className="text-gray-400 text-xs">{item.description}</p>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </section>
            )}
          </div>
        )}

        {!selectedLibrary && !loading && (
          <div className="text-center py-20 text-gray-500 text-sm">
            Select a library above to view compliance requirements.
          </div>
        )}
      </div>
    </div>
  );
}
