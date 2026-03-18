/**
 * LivePlayground — inline doc query demo for the landing page.
 * Works without auth (uses anonymous free tier).
 */
"use client";

import { useState } from "react";
import { queryDocs } from "@/lib/api";

const EXAMPLE_QUERIES = [
  { lib: "/razorpay/razorpay-sdk", q: "create payment link", label: "Razorpay" },
  { lib: "/zerodha/kite-api", q: "place market order", label: "Zerodha Kite" },
  { lib: "/ondc/protocol-specs", q: "search request flow", label: "ONDC" },
  { lib: "/vercel/next.js", q: "server actions", label: "Next.js" },
  { lib: "/npci/upi-specs", q: "collect request API", label: "UPI/NPCI" },
];

export function LivePlayground() {
  const [libraryId, setLibraryId] = useState("/razorpay/razorpay-sdk");
  const [query, setQuery] = useState("create payment link with expiry");
  const [result, setResult] = useState<string | null>(null);
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasQueried, setHasQueried] = useState(false);

  async function handleQuery() {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setHasQueried(true);
    try {
      const data = await queryDocs({ libraryId, query, tokenBudget: 3000 });
      setResult(data.docs);
      setSources(data.sources);
    } catch {
      setError("Backend not connected — deploy to see live results. This is a demo of the interface.");
      setResult(DEMO_RESULT);
      setSources(["https://razorpay.com/docs/api/payment-links/"]);
    } finally {
      setLoading(false);
    }
  }

  function selectExample(lib: string, q: string) {
    setLibraryId(lib);
    setQuery(q);
    setResult(null);
    setHasQueried(false);
  }

  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3 border-b border-[#1e2d44] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500/60" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
          <div className="w-3 h-3 rounded-full bg-green-500/60" />
          <span className="text-gray-500 text-xs ml-2 font-mono">contextBharat playground</span>
        </div>
        <span className="text-gray-600 text-xs">no signup required</span>
      </div>

      {/* Quick examples */}
      <div className="px-5 py-3 border-b border-[#1e2d44] flex gap-2 overflow-x-auto">
        {EXAMPLE_QUERIES.map(({ lib, q, label }) => (
          <button
            key={lib}
            onClick={() => selectExample(lib, q)}
            className={`text-xs px-3 py-1.5 rounded-lg whitespace-nowrap transition-colors ${
              libraryId === lib
                ? "bg-[#f59e1c]/15 text-[#f59e1c] border border-[#f59e1c]/30"
                : "bg-white/5 text-gray-400 border border-transparent hover:text-white"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-5">
        <div className="flex gap-2 mb-1">
          <div className="flex-1">
            <div className="text-gray-500 text-xs mb-1.5 font-mono">Library</div>
            <input
              value={libraryId}
              onChange={(e) => setLibraryId(e.target.value)}
              className="w-full bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2 text-sm text-white font-mono placeholder-gray-600 focus:outline-none focus:border-[#f59e1c]"
            />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-gray-500 text-xs mb-1.5 font-mono">Query</div>
          <div className="flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleQuery()}
              placeholder="Ask anything about this library..."
              className="flex-1 bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#f59e1c]"
            />
            <button
              onClick={handleQuery}
              disabled={loading || !query}
              className="bg-[#f59e1c] text-black px-6 py-2.5 rounded-lg text-sm font-semibold hover:bg-[#fbbf45] disabled:opacity-50 transition-colors whitespace-nowrap"
            >
              {loading ? "Fetching..." : "Query Docs"}
            </button>
          </div>
        </div>
      </div>

      {/* Result */}
      <div className="border-t border-[#1e2d44] p-5 min-h-[200px] max-h-[400px] overflow-y-auto">
        {loading && (
          <div className="flex items-center gap-3 text-gray-400 text-sm">
            <div className="w-4 h-4 border-2 border-[#f59e1c] border-t-transparent rounded-full animate-spin" />
            Searching documentation...
          </div>
        )}
        {error && !result && (
          <div className="text-amber-400 text-sm bg-amber-500/10 p-3 rounded-lg">{error}</div>
        )}
        {result && (
          <div>
            <pre className="text-gray-300 text-xs leading-relaxed whitespace-pre-wrap font-mono">
              {result}
            </pre>
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
                    {new URL(src).hostname}
                  </a>
                ))}
              </div>
            )}
          </div>
        )}
        {!loading && !result && !hasQueried && (
          <div className="text-center py-8">
            <div className="text-gray-500 text-sm mb-2">
              Pick a library above and hit <span className="text-[#f59e1c] font-semibold">Query Docs</span>
            </div>
            <div className="text-gray-600 text-xs">
              This is exactly what your AI assistant gets when you type <code className="text-gray-400">use contextbharat</code>
            </div>
          </div>
        )}
      </div>
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
  amount: 50000, // amount in paise (₹500)
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
