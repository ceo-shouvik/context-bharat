/**
 * Developer Tools Hub — code snippets, test gen, OpenAPI gen, SDK gen in one place.
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { features } from "@/lib/features";
import { getLibraries, type Library } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.contextbharat.com";

/* -------------------------------------------------------------------------- */
/*  Shared helpers                                                            */
/* -------------------------------------------------------------------------- */

function SectionPlaceholder({ title }: { title: string }) {
  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-6 text-center">
      <p className="text-gray-500 text-sm">{title} — Coming Soon</p>
    </div>
  );
}

function LibraryDropdown({
  libraries,
  value,
  onChange,
}: {
  libraries: Library[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-[#0c1120] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 w-full focus:border-[#f59e1c] focus:outline-none"
    >
      <option value="">Select a library</option>
      {libraries.map((lib) => (
        <option key={lib.library_id} value={lib.library_id}>
          {lib.name}
        </option>
      ))}
    </select>
  );
}

function CodeOutput({
  code,
  loading,
  error,
}: {
  code: string | null;
  loading: boolean;
  error: string | null;
}) {
  if (loading) {
    return (
      <div className="bg-black/40 rounded-lg p-4 text-sm text-gray-400 font-mono animate-pulse">
        Generating...
      </div>
    );
  }
  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-sm text-red-400">
        {error}
      </div>
    );
  }
  if (!code) return null;
  return (
    <pre className="bg-black/40 rounded-lg p-4 text-sm text-green-300 font-mono overflow-x-auto max-h-[500px] overflow-y-auto">
      <code>{code}</code>
    </pre>
  );
}

/* -------------------------------------------------------------------------- */
/*  Code Snippet Generator                                                     */
/* -------------------------------------------------------------------------- */

function CodeSnippetSection({ libraries }: { libraries: Library[] }) {
  const [libraryId, setLibraryId] = useState("");
  const [task, setTask] = useState("");
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    if (!libraryId || !task) return;
    setLoading(true);
    setError(null);
    setCode(null);
    try {
      const res = await fetch(`${API_BASE}/v1/tools/code-snippet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ library_id: libraryId, task, language }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setCode(data.code ?? data.snippet ?? JSON.stringify(data, null, 2));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  if (!features.codeSnippets) return <SectionPlaceholder title="Code Snippet Generator" />;

  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
      <h3 className="text-white font-medium mb-4">Code Snippet Generator</h3>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-4">
        <LibraryDropdown libraries={libraries} value={libraryId} onChange={setLibraryId} />
        <input
          type="text"
          placeholder="Task (e.g., create payment link)"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          className="bg-[#0c1120] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 focus:border-[#f59e1c] focus:outline-none"
        />
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="bg-[#0c1120] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 focus:border-[#f59e1c] focus:outline-none"
        >
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="go">Go</option>
        </select>
        <button
          onClick={generate}
          disabled={!libraryId || !task || loading}
          className="bg-[#f59e1c] text-black text-sm font-medium rounded-lg px-4 py-2 hover:bg-[#f59e1c]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Generate
        </button>
      </div>
      <CodeOutput code={code} loading={loading} error={error} />
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  Test Generator                                                             */
/* -------------------------------------------------------------------------- */

function TestGeneratorSection({ libraries }: { libraries: Library[] }) {
  const [libraryId, setLibraryId] = useState("");
  const [framework, setFramework] = useState("pytest");
  const [code, setCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    if (!libraryId) return;
    setLoading(true);
    setError(null);
    setCode(null);
    try {
      const res = await fetch(`${API_BASE}/v1/tools/test-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ library_id: libraryId, framework }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setCode(data.code ?? data.tests ?? JSON.stringify(data, null, 2));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  if (!features.testGeneration) return <SectionPlaceholder title="Test Generator" />;

  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
      <h3 className="text-white font-medium mb-4">Test Generator</h3>
      <div className="grid gap-3 sm:grid-cols-3 mb-4">
        <LibraryDropdown libraries={libraries} value={libraryId} onChange={setLibraryId} />
        <select
          value={framework}
          onChange={(e) => setFramework(e.target.value)}
          className="bg-[#0c1120] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 focus:border-[#f59e1c] focus:outline-none"
        >
          <option value="pytest">pytest</option>
          <option value="jest">jest</option>
        </select>
        <button
          onClick={generate}
          disabled={!libraryId || loading}
          className="bg-[#f59e1c] text-black text-sm font-medium rounded-lg px-4 py-2 hover:bg-[#f59e1c]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Generate Tests
        </button>
      </div>
      <CodeOutput code={code} loading={loading} error={error} />
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  OpenAPI Generator                                                          */
/* -------------------------------------------------------------------------- */

function OpenAPISection({ libraries }: { libraries: Library[] }) {
  const [libraryId, setLibraryId] = useState("");
  const [code, setCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    if (!libraryId) return;
    setLoading(true);
    setError(null);
    setCode(null);
    try {
      const res = await fetch(`${API_BASE}/v1/tools/openapi-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ library_id: libraryId }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setCode(
        typeof data.spec === "string"
          ? data.spec
          : JSON.stringify(data.spec ?? data, null, 2),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  if (!features.openapiGeneration) return <SectionPlaceholder title="OpenAPI Generator" />;

  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
      <h3 className="text-white font-medium mb-4">OpenAPI Spec Generator</h3>
      <div className="grid gap-3 sm:grid-cols-2 mb-4">
        <LibraryDropdown libraries={libraries} value={libraryId} onChange={setLibraryId} />
        <button
          onClick={generate}
          disabled={!libraryId || loading}
          className="bg-[#f59e1c] text-black text-sm font-medium rounded-lg px-4 py-2 hover:bg-[#f59e1c]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Generate OpenAPI Spec
        </button>
      </div>
      <CodeOutput code={code} loading={loading} error={error} />
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  SDK Generator                                                              */
/* -------------------------------------------------------------------------- */

function SDKSection({ libraries }: { libraries: Library[] }) {
  const [libraryId, setLibraryId] = useState("");
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    if (!libraryId) return;
    setLoading(true);
    setError(null);
    setCode(null);
    try {
      const res = await fetch(`${API_BASE}/v1/tools/sdk-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ library_id: libraryId, language }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setCode(data.code ?? data.sdk ?? JSON.stringify(data, null, 2));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  if (!features.sdkGeneration) return <SectionPlaceholder title="SDK Generator" />;

  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
      <h3 className="text-white font-medium mb-4">SDK Generator</h3>
      <div className="grid gap-3 sm:grid-cols-3 mb-4">
        <LibraryDropdown libraries={libraries} value={libraryId} onChange={setLibraryId} />
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="bg-[#0c1120] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 focus:border-[#f59e1c] focus:outline-none"
        >
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="go">Go</option>
        </select>
        <button
          onClick={generate}
          disabled={!libraryId || loading}
          className="bg-[#f59e1c] text-black text-sm font-medium rounded-lg px-4 py-2 hover:bg-[#f59e1c]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Generate SDK
        </button>
      </div>
      <CodeOutput code={code} loading={loading} error={error} />
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  Main Page                                                                  */
/* -------------------------------------------------------------------------- */

export default function ToolsPage() {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [loadingLibs, setLoadingLibs] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const libs = await getLibraries();
        setLibraries(libs);
      } catch {
        // Libraries list is non-critical; tools still render with empty dropdown
      } finally {
        setLoadingLibs(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-[#05080f]"><title>Developer Tools — contextBharat</title>
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-10">
          <h1 className="text-white text-2xl font-semibold">Developer Tools</h1>
          <p className="text-gray-400 text-sm mt-1">
            Generate code snippets, tests, OpenAPI specs, and SDKs for any indexed library
          </p>
        </div>

        {loadingLibs && (
          <div className="text-gray-400 text-sm mb-6">Loading libraries...</div>
        )}

        <div className="grid gap-6">
          <CodeSnippetSection libraries={libraries} />
          <TestGeneratorSection libraries={libraries} />
          <OpenAPISection libraries={libraries} />
          <SDKSection libraries={libraries} />
        </div>
      </div>
    </div>
  );
}
