/**
 * LivePlayground — inline doc query demo for the landing page.
 * Works without auth (uses anonymous free tier).
 * Library selection via dropdown, query via predefined options or custom.
 */
"use client";

import { useState } from "react";
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

export function LivePlayground() {
  const [libraryId, setLibraryId] = useState("/razorpay/razorpay-sdk");
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasQueried, setHasQueried] = useState(false);

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
      const data = await queryDocs({ libraryId, query: finalQuery, tokenBudget: 3000 });
      setResult(data.docs);
      setSources(data.sources);
    } catch {
      setError("Backend not connected — showing demo result.");
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

      {/* Library + Query selectors */}
      <div className="p-5">
        {/* Library dropdown */}
        <div className="mb-4">
          <div className="text-gray-500 text-xs mb-1.5">Select Library</div>
          <select
            value={libraryId}
            onChange={(e) => handleLibraryChange(e.target.value)}
            className="w-full bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-[#f59e1c] appearance-none cursor-pointer"
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
          <div className="text-gray-500 text-xs mb-2">Ask a question about {selectedLib?.name ?? "this library"}</div>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => handleQuery(s)}
                disabled={loading}
                className={`text-xs px-3 py-1.5 rounded-lg transition-colors border ${
                  query === s
                    ? "bg-[#f59e1c]/15 text-[#f59e1c] border-[#f59e1c]/30"
                    : "bg-white/5 text-gray-400 border-white/5 hover:text-white hover:border-white/20"
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
            className="flex-1 bg-[#131e30] border border-[#253650] rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#f59e1c]"
          />
          <button
            onClick={() => handleQuery()}
            disabled={loading || !query}
            className="bg-[#f59e1c] text-black px-6 py-2.5 rounded-lg text-sm font-semibold hover:bg-[#fbbf45] disabled:opacity-50 transition-colors whitespace-nowrap"
          >
            {loading ? "Fetching..." : "Query Docs"}
          </button>
        </div>
      </div>

      {/* Result */}
      <div className="border-t border-[#1e2d44] p-5 min-h-[200px] max-h-[400px] overflow-y-auto">
        {loading && (
          <div className="flex items-center gap-3 text-gray-400 text-sm">
            <div className="w-4 h-4 border-2 border-[#f59e1c] border-t-transparent rounded-full animate-spin" />
            Searching {selectedLib?.name} documentation...
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
                    {(() => { try { return new URL(src).hostname; } catch { return src; } })()}
                  </a>
                ))}
              </div>
            )}
          </div>
        )}
        {!loading && !result && !hasQueried && (
          <div className="text-center py-8">
            <div className="text-gray-500 text-sm mb-2">
              Select a library and click a question to see real documentation
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
