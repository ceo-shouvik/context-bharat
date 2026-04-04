/**
 * LivePlayground — inline doc query demo for the landing page.
 * Works without auth (uses anonymous free tier).
 * Features: library selector, query suggestions, copy button on results,
 * loading skeleton, language selector, formatted markdown output.
 */
"use client";

import { useState, useCallback } from "react";
import { queryDocs } from "@/lib/api";

const LIBRARIES = [
  { id: "/razorpay/razorpay-sdk", name: "Razorpay", category: "Fintech" },
  { id: "/cashfree/cashfree-pg", name: "Cashfree PG", category: "Fintech" },
  { id: "/setu/setu-docs", name: "Setu APIs", category: "Fintech" },
  { id: "/juspay/hyperswitch", name: "Juspay HyperSwitch", category: "Fintech" },
  { id: "/zerodha/kite-api", name: "Zerodha Kite", category: "Trading" },
  { id: "/upstox/upstox-api", name: "Upstox API", category: "Trading" },
  { id: "/ondc/protocol-specs", name: "ONDC Protocol", category: "India DPI" },
  { id: "/npci/upi-specs", name: "UPI / NPCI", category: "India DPI" },
  { id: "/gstn/gst-api", name: "GSTN API", category: "India DPI" },
  { id: "/bhashini/bhashini-api", name: "Bhashini API", category: "Indian AI" },
  { id: "/sarvam/sarvam-api", name: "Sarvam AI", category: "Indian AI" },
  { id: "/zoho/zoho-crm-api", name: "Zoho CRM", category: "Enterprise" },
  { id: "/frappe/frappe-framework", name: "Frappe / ERPNext", category: "Enterprise" },
  { id: "/vercel/next.js", name: "Next.js", category: "Framework" },
  { id: "/tiangolo/fastapi", name: "FastAPI", category: "Framework" },
  { id: "/django/django", name: "Django", category: "Framework" },
  { id: "/facebook/react", name: "React", category: "Framework" },
  { id: "/flutter/flutter", name: "Flutter", category: "Framework" },
  { id: "/stripe/stripe-api", name: "Stripe", category: "Global" },
];

const QUERY_SUGGESTIONS: Record<string, string[]> = {
  "/razorpay/razorpay-sdk": [
    "Create payment link with expiry",
    "Handle webhook verification",
    "Create subscription plan",
    "Process refund for an order",
    "UPI payment integration",
  ],
  "/zerodha/kite-api": [
    "Place market order",
    "Get live stock quote",
    "WebSocket streaming setup",
    "Login and session management",
    "Get order history",
  ],
  "/ondc/protocol-specs": [
    "Search request flow",
    "Confirm order sequence",
    "Beckn protocol authentication",
    "Buyer app integration steps",
    "Track order status",
  ],
  "/npci/upi-specs": [
    "Collect request API",
    "Transaction status check",
    "Mandate creation flow",
    "QR code payment",
    "Dispute resolution API",
  ],
  "/vercel/next.js": [
    "Server actions example",
    "App router middleware",
    "Dynamic route params",
    "API route handler",
    "Image optimization",
  ],
  "/cashfree/cashfree-pg": [
    "Create payment order",
    "Verify payment signature",
    "Subscription setup",
    "Payout to bank account",
  ],
  "/setu/setu-docs": [
    "Account Aggregator flow",
    "UPI DeepLink creation",
    "BBPS bill payment",
  ],
  "/gstn/gst-api": [
    "File GSTR-1 return",
    "Verify GSTIN number",
    "E-way bill generation",
  ],
};

const DEFAULT_QUERIES = [
  "Authentication and setup",
  "Create a basic request",
  "Handle errors and retries",
  "Webhook integration",
];

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ta", label: "Tamil" },
  { code: "te", label: "Telugu" },
];

export function LivePlayground() {
  const [libraryId, setLibraryId] = useState("/razorpay/razorpay-sdk");
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("en");
  const [result, setResult] = useState<string | null>(null);
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasQueried, setHasQueried] = useState(false);
  const [resultCopied, setResultCopied] = useState(false);

  const suggestions = QUERY_SUGGESTIONS[libraryId] ?? DEFAULT_QUERIES;
  const selectedLib = LIBRARIES.find((l) => l.id === libraryId);

  async function handleQuery(q?: string) {
    const finalQuery = q ?? query;
    if (!finalQuery.trim()) return;
    if (q) setQuery(q);
    setLoading(true);
    setError(null);
    setResult(null);
    setHasQueried(true);
    try {
      const data = await queryDocs({ libraryId, query: finalQuery, tokenBudget: 3000, language });
      setResult(data.docs);
      setSources(data.sources);
    } catch {
      setError("Backend not connected \u2014 showing demo result.");
      setResult(DEMO_RESULT);
      setSources(["https://razorpay.com/docs/api/payment-links/"]);
    } finally {
      setLoading(false);
    }
  }

  function handleLibraryChange(newLib: string) {
    setLibraryId(newLib);
    setQuery("");
    setResult(null);
    setHasQueried(false);
    setError(null);
  }

  const handleCopyResult = useCallback(async () => {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(result);
      setResultCopied(true);
      setTimeout(() => setResultCopied(false), 2000);
    } catch {
      // Silent fail
    }
  }, [result]);

  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-2xl overflow-hidden shadow-2xl shadow-black/20">
      {/* Header bar */}
      <div className="px-5 py-3 border-b border-[#1e2d44] flex items-center justify-between bg-[#0a0e1a]">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500/60" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
          <div className="w-3 h-3 rounded-full bg-green-500/60" />
          <span className="text-gray-500 text-xs ml-2 font-mono">contextBharat playground</span>
        </div>
        <div className="flex items-center gap-3">
          {/* Language selector */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-[#131e30] border border-[#253650] rounded-md px-2 py-1 text-xs text-gray-400 focus:outline-none focus:border-[#f59e1c] appearance-none cursor-pointer"
            style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M2 4l4 4 4-4'/%3E%3C/svg%3E")`, backgroundRepeat: "no-repeat", backgroundPosition: "right 6px center", paddingRight: "20px" }}
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>{l.label}</option>
            ))}
          </select>
          <span className="text-gray-600 text-xs">no signup required</span>
        </div>
      </div>

      {/* Controls */}
      <div className="p-5">
        {/* Library dropdown */}
        <div className="mb-4">
          <div className="text-gray-500 text-xs mb-1.5 font-medium">Select Library</div>
          <select
            value={libraryId}
            onChange={(e) => handleLibraryChange(e.target.value)}
            className="w-full bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-[#f59e1c] appearance-none cursor-pointer transition-colors"
            style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M2 4l4 4 4-4'/%3E%3C/svg%3E")`, backgroundRepeat: "no-repeat", backgroundPosition: "right 12px center" }}
          >
            <optgroup label="Indian Fintech">
              {LIBRARIES.filter((l) => l.category === "Fintech").map((l) => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </optgroup>
            <optgroup label="Trading APIs">
              {LIBRARIES.filter((l) => l.category === "Trading").map((l) => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </optgroup>
            <optgroup label="India Stack / DPI">
              {LIBRARIES.filter((l) => l.category === "India DPI").map((l) => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </optgroup>
            <optgroup label="Indian AI">
              {LIBRARIES.filter((l) => l.category === "Indian AI").map((l) => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </optgroup>
            <optgroup label="Enterprise India">
              {LIBRARIES.filter((l) => l.category === "Enterprise").map((l) => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </optgroup>
            <optgroup label="Global Frameworks">
              {LIBRARIES.filter((l) => l.category === "Framework").map((l) => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </optgroup>
            <optgroup label="Global SaaS">
              {LIBRARIES.filter((l) => l.category === "Global").map((l) => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </optgroup>
          </select>
        </div>

        {/* Query suggestions */}
        <div className="mb-4">
          <div className="text-gray-500 text-xs mb-2 font-medium">
            Ask a question about {selectedLib?.name ?? "this library"}
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => handleQuery(s)}
                disabled={loading}
                className={`text-xs px-3 py-1.5 rounded-lg transition-all border ${
                  query === s
                    ? "bg-[#f59e1c]/15 text-[#f59e1c] border-[#f59e1c]/30"
                    : "bg-white/5 text-gray-400 border-white/5 hover:text-white hover:border-white/20 hover:bg-white/10"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Custom query input */}
        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
            placeholder="Or type your own question..."
            className="flex-1 bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#f59e1c] transition-colors"
          />
          <button
            onClick={() => handleQuery()}
            disabled={loading || !query}
            className="bg-[#f59e1c] text-black px-6 py-2.5 rounded-lg text-sm font-semibold hover:bg-[#fbbf45] disabled:opacity-50 transition-all whitespace-nowrap"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                Fetching
              </span>
            ) : (
              "Query Docs"
            )}
          </button>
        </div>
      </div>

      {/* Result panel */}
      <div className="border-t border-[#1e2d44] min-h-[200px] max-h-[500px] overflow-y-auto relative">
        {/* Loading skeleton */}
        {loading && (
          <div className="p-5 space-y-3">
            <div className="flex items-center gap-3 text-gray-400 text-sm mb-4">
              <div className="w-4 h-4 border-2 border-[#f59e1c] border-t-transparent rounded-full animate-spin" />
              Searching {selectedLib?.name} documentation...
            </div>
            <div className="space-y-2.5 animate-pulse">
              <div className="h-4 bg-white/5 rounded w-3/4" />
              <div className="h-3 bg-white/5 rounded w-full" />
              <div className="h-3 bg-white/5 rounded w-5/6" />
              <div className="h-24 bg-white/[0.03] rounded-lg mt-3" />
              <div className="h-3 bg-white/5 rounded w-2/3" />
              <div className="h-3 bg-white/5 rounded w-4/5" />
            </div>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="px-5 pt-4">
            <div className="text-amber-400 text-sm bg-amber-500/10 border border-amber-500/20 p-3 rounded-lg">
              {error}
            </div>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <div className="relative group">
            {/* Copy button for result */}
            <div className="absolute top-3 right-3 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={handleCopyResult}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                  resultCopied
                    ? "bg-green-500/15 text-green-400 border border-green-500/30"
                    : "bg-[#131e30] text-gray-400 border border-[#253650] hover:text-white hover:bg-[#1a2840]"
                }`}
              >
                {resultCopied ? (
                  <>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                    Copied!
                  </>
                ) : (
                  <>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                    </svg>
                    Copy
                  </>
                )}
              </button>
            </div>

            <div className="p-5">
              <PlaygroundResult content={result} />
              {sources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-[#1e2d44] flex items-center gap-2 flex-wrap">
                  <span className="text-gray-600 text-xs">Sources:</span>
                  {sources.map((src) => (
                    <a
                      key={src}
                      href={src}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-[#f59e1c] hover:underline"
                    >
                      {(() => { try { return new URL(src).hostname; } catch { return src; } })()}
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Empty state */}
        {!loading && !result && !hasQueried && (
          <div className="text-center py-12 px-5">
            <div className="w-12 h-12 rounded-full bg-[#f59e1c]/10 flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-[#f59e1c]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </div>
            <div className="text-gray-400 text-sm mb-2">
              Select a library and click a question to see real documentation
            </div>
            <div className="text-gray-600 text-xs">
              This is exactly what your AI assistant gets when you type{" "}
              <code className="text-[#f59e1c] font-medium">use contextbharat</code>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * PlaygroundResult — renders the markdown-like response with basic formatting.
 * Handles headings, code blocks, tables, and paragraphs.
 */
function PlaygroundResult({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Code block
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      elements.push(
        <PlaygroundCodeBlock
          key={`code-${elements.length}`}
          code={codeLines.join("\n")}
          language={lang}
        />
      );
      continue;
    }

    // Heading
    if (line.startsWith("## ")) {
      elements.push(
        <h3 key={`h-${i}`} className="text-white font-semibold text-sm mt-4 mb-2">
          {line.slice(3)}
        </h3>
      );
      i++;
      continue;
    }
    if (line.startsWith("### ")) {
      elements.push(
        <h4 key={`h-${i}`} className="text-white font-medium text-xs mt-3 mb-1.5 uppercase tracking-wide">
          {line.slice(4)}
        </h4>
      );
      i++;
      continue;
    }

    // Table row
    if (line.includes("|") && line.trim().startsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].includes("|") && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      elements.push(
        <div key={`table-${elements.length}`} className="overflow-x-auto my-3">
          <table className="text-xs text-gray-400 w-full">
            <tbody>
              {tableLines
                .filter((row) => !row.match(/^\|[\s-|]+$/))
                .map((row, ri) => (
                  <tr key={ri} className={ri === 0 ? "text-gray-300 font-medium" : ""}>
                    {row
                      .split("|")
                      .filter(Boolean)
                      .map((cell, ci) => (
                        <td key={ci} className="px-2 py-1.5 border-b border-[#1e2d44]/50">
                          {cell.trim()}
                        </td>
                      ))}
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Empty line
    if (line.trim() === "") {
      i++;
      continue;
    }

    // Regular text
    elements.push(
      <p key={`p-${i}`} className="text-gray-300 text-xs leading-relaxed mb-1.5">
        {line}
      </p>
    );
    i++;
  }

  return <div>{elements}</div>;
}

/**
 * Inline code block with copy button for the playground result.
 */
function PlaygroundCodeBlock({ code, language }: { code: string; language: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Silent fail
    }
  };

  return (
    <div className="group/code relative my-3 bg-[#0a0e1a] border border-[#1e2d44]/60 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#1e2d44]/40">
        {language && (
          <span className="text-[10px] font-mono text-gray-600 uppercase tracking-wide">
            {language}
          </span>
        )}
        <button
          onClick={handleCopy}
          className={`flex items-center gap-1 text-[10px] px-2 py-0.5 rounded transition-all ${
            copied
              ? "text-green-400"
              : "text-gray-600 hover:text-gray-300 opacity-0 group-hover/code:opacity-100"
          }`}
        >
          {copied ? (
            <>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
              Copied
            </>
          ) : (
            <>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
              Copy
            </>
          )}
        </button>
      </div>
      <pre className="p-3 overflow-x-auto text-xs leading-relaxed">
        <code className="font-mono text-green-300/90">{code}</code>
      </pre>
    </div>
  );
}

const DEMO_RESULT = `## Create a Payment Link

Use the Payment Links API to create a shareable link for collecting payments.

\`\`\`javascript
const Razorpay = require('razorpay');

const instance = new Razorpay({
  key_id: 'YOUR_KEY_ID',
  key_secret: 'YOUR_KEY_SECRET',
});

const paymentLink = await instance.paymentLink.create({
  amount: 50000, // amount in paise (\u20B9500)
  currency: 'INR',
  accept_partial: true,
  first_min_partial_amount: 10000,
  description: 'For XYZ purpose',
  customer: {
    name: 'Gaurav Kumar',
    email: 'gaurav.kumar@example.com',
    contact: '+919999999999',
  },
  notify: { sms: true, email: true },
  reminder_enable: true,
  callback_url: 'https://example.com/callback',
  callback_method: 'get',
});

console.log(paymentLink.short_url);
// https://rzp.io/i/abc123
\`\`\`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| amount | integer | Yes | Amount in paise |
| currency | string | Yes | ISO currency code (INR) |
| description | string | No | Purpose of payment |
| customer | object | No | Customer details |
| expire_by | integer | No | Unix timestamp for expiry |

### Webhooks

Listen for \`payment_link.paid\` event to confirm payment completion.`;
