/**
 * Framework Starters — pre-built starter templates for Indian API integrations.
 */
"use client";

import { useEffect, useState } from "react";
import { features } from "@/lib/features";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.contextbharat.com";

interface StarterFile {
  path: string;
  code: string;
}

interface Starter {
  id: string;
  framework: string;
  name: string;
  description: string;
  apis_used: string[];
  files?: StarterFile[];
  file_tree?: string;
}

function ComingSoon() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">&#128640;</div>
        <h2 className="text-white text-xl font-semibold mb-2">
          Framework Starters — Coming Soon
        </h2>
        <p className="text-gray-400 text-sm max-w-md">
          Ready-to-use starter templates for Next.js + Razorpay, Django + ONDC,
          FastAPI + UPI, and more.
        </p>
      </div>
    </div>
  );
}

export default function StartersPage() {
  const [starters, setStarters] = useState<Starter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [activeFile, setActiveFile] = useState<string | null>(null);

  useEffect(() => {
    if (!features.frameworkStarters) return;

    async function fetchStarters() {
      try {
        const res = await fetch(`${API_BASE}/v1/starters`);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        const data = await res.json();
        setStarters(data.starters ?? data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load starters");
      } finally {
        setLoading(false);
      }
    }

    fetchStarters();
  }, []);

  if (!features.frameworkStarters) {
    return (
      <div className="min-h-screen bg-[#05080f]"><title>Starters — contextBharat</title>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <ComingSoon />
        </div>
      </div>
    );
  }

  function handleExpand(starter: Starter) {
    if (expandedId === starter.id) {
      setExpandedId(null);
      setActiveFile(null);
    } else {
      setExpandedId(starter.id);
      setActiveFile(starter.files?.[0]?.path ?? null);
    }
  }

  return (
    <div className="min-h-screen bg-[#05080f]"><title>Starters — contextBharat</title>
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-10">
          <h1 className="text-white text-2xl font-semibold">Framework Starters</h1>
          <p className="text-gray-400 text-sm mt-1">
            Production-ready starter templates for Indian API integrations
          </p>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-gray-400 text-sm">Loading starters...</div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm">
            {error}
          </div>
        )}

        {!loading && !error && starters.length === 0 && (
          <div className="text-center py-20 text-gray-500 text-sm">
            No starters available yet. Check back soon.
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {starters.map((starter) => (
            <div
              key={starter.id}
              className={`bg-[#0c1120] border rounded-xl p-5 cursor-pointer transition-all hover:border-[#f59e1c]/50 ${
                expandedId === starter.id
                  ? "border-[#f59e1c]/60 md:col-span-2 lg:col-span-3"
                  : "border-[#1e2d44]"
              }`}
              onClick={() => handleExpand(starter)}
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <h3 className="text-white font-medium">{starter.name}</h3>
                <span className="text-xs bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-full px-2 py-0.5 whitespace-nowrap">
                  {starter.framework}
                </span>
              </div>
              <p className="text-gray-400 text-sm mb-3">{starter.description}</p>
              <div className="flex flex-wrap gap-1.5">
                {starter.apis_used.map((api) => (
                  <span
                    key={api}
                    className="text-xs bg-[#f59e1c]/10 text-[#f59e1c] border border-[#f59e1c]/20 rounded px-2 py-0.5"
                  >
                    {api}
                  </span>
                ))}
              </div>

              {expandedId === starter.id && (
                <div
                  className="mt-5 pt-5 border-t border-[#1e2d44]"
                  onClick={(e) => e.stopPropagation()}
                >
                  {starter.file_tree && (
                    <div className="mb-4">
                      <h4 className="text-white text-sm font-medium mb-2">File Tree</h4>
                      <pre className="bg-black/40 rounded-lg p-4 text-sm text-gray-300 font-mono overflow-x-auto">
                        {starter.file_tree}
                      </pre>
                    </div>
                  )}

                  {starter.files && starter.files.length > 0 && (
                    <div>
                      <h4 className="text-white text-sm font-medium mb-2">Files</h4>
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {starter.files.map((file) => (
                          <button
                            key={file.path}
                            onClick={() => setActiveFile(file.path)}
                            className={`text-xs px-2.5 py-1 rounded border transition-colors ${
                              activeFile === file.path
                                ? "bg-[#f59e1c]/20 text-[#f59e1c] border-[#f59e1c]/40"
                                : "bg-[#0c1120] text-gray-400 border-[#1e2d44] hover:text-white"
                            }`}
                          >
                            {file.path}
                          </button>
                        ))}
                      </div>
                      {starter.files
                        .filter((f) => f.path === activeFile)
                        .map((file) => (
                          <pre
                            key={file.path}
                            className="bg-black/40 rounded-lg p-4 text-sm text-green-300 font-mono overflow-x-auto"
                          >
                            <code>{file.code}</code>
                          </pre>
                        ))}
                    </div>
                  )}

                  {!starter.file_tree && (!starter.files || starter.files.length === 0) && (
                    <p className="text-gray-500 text-sm">
                      Template files coming soon.
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
