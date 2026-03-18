/**
 * Integration Cookbooks — step-by-step integration guides combining multiple APIs.
 */
"use client";

import { useEffect, useState } from "react";
import { features } from "@/lib/features";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.contextbharat.com";

interface Cookbook {
  id: string;
  title: string;
  description: string;
  apis_used: string[];
  difficulty: "beginner" | "intermediate" | "advanced";
  flow?: string;
  code_examples?: { language: string; code: string }[];
}

const difficultyColor: Record<string, string> = {
  beginner: "bg-green-500/20 text-green-400 border-green-500/30",
  intermediate: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  advanced: "bg-red-500/20 text-red-400 border-red-500/30",
};

function ComingSoon() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">&#128218;</div>
        <h2 className="text-white text-xl font-semibold mb-2">
          Integration Cookbooks — Coming Soon
        </h2>
        <p className="text-gray-400 text-sm max-w-md">
          Step-by-step guides for combining Indian APIs into real-world integrations.
          Razorpay + ONDC, Zerodha + Account Aggregator, and more.
        </p>
      </div>
    </div>
  );
}

export default function CookbooksPage() {
  const [cookbooks, setCookbooks] = useState<Cookbook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (!features.cookbooks) return;

    async function fetchCookbooks() {
      try {
        const res = await fetch(`${API_BASE}/v1/cookbooks`);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        const data = await res.json();
        setCookbooks(data.cookbooks ?? data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load cookbooks");
      } finally {
        setLoading(false);
      }
    }

    fetchCookbooks();
  }, []);

  if (!features.cookbooks) {
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
          <h1 className="text-white text-2xl font-semibold">Integration Cookbooks</h1>
          <p className="text-gray-400 text-sm mt-1">
            End-to-end integration guides combining multiple Indian APIs
          </p>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-gray-400 text-sm">Loading cookbooks...</div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm">
            {error}
          </div>
        )}

        {!loading && !error && cookbooks.length === 0 && (
          <div className="text-center py-20 text-gray-500 text-sm">
            No cookbooks available yet. Check back soon.
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {cookbooks.map((cookbook) => (
            <div
              key={cookbook.id}
              className={`bg-[#0c1120] border rounded-xl p-5 cursor-pointer transition-all hover:border-[#f59e1c]/50 ${
                expandedId === cookbook.id
                  ? "border-[#f59e1c]/60 md:col-span-2 lg:col-span-3"
                  : "border-[#1e2d44]"
              }`}
              onClick={() => setExpandedId(expandedId === cookbook.id ? null : cookbook.id)}
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <h3 className="text-white font-medium">{cookbook.title}</h3>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full border whitespace-nowrap ${
                    difficultyColor[cookbook.difficulty] ?? difficultyColor.beginner
                  }`}
                >
                  {cookbook.difficulty}
                </span>
              </div>
              <p className="text-gray-400 text-sm mb-3">{cookbook.description}</p>
              <div className="flex flex-wrap gap-1.5">
                {cookbook.apis_used.map((api) => (
                  <span
                    key={api}
                    className="text-xs bg-[#f59e1c]/10 text-[#f59e1c] border border-[#f59e1c]/20 rounded px-2 py-0.5"
                  >
                    {api}
                  </span>
                ))}
              </div>

              {expandedId === cookbook.id && (
                <div className="mt-5 pt-5 border-t border-[#1e2d44]">
                  {cookbook.flow && (
                    <div className="mb-4">
                      <h4 className="text-white text-sm font-medium mb-2">Integration Flow</h4>
                      <pre className="bg-black/40 rounded-lg p-4 text-sm text-gray-300 font-mono overflow-x-auto whitespace-pre-wrap">
                        {cookbook.flow}
                      </pre>
                    </div>
                  )}
                  {cookbook.code_examples?.map((ex, i) => (
                    <div key={i} className="mb-4">
                      <h4 className="text-white text-sm font-medium mb-2">
                        Code Example ({ex.language})
                      </h4>
                      <pre className="bg-black/40 rounded-lg p-4 text-sm text-green-300 font-mono overflow-x-auto">
                        <code>{ex.code}</code>
                      </pre>
                    </div>
                  ))}
                  {!cookbook.flow && !cookbook.code_examples?.length && (
                    <p className="text-gray-500 text-sm">
                      Detailed guide coming soon.
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
