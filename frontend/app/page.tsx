/**
 * Landing page — context7india.com
 * Copy sourced from website/content.md
 */
import Link from "next/link";

export const metadata = {
  title: "Context7 India — AI Documentation for Indian APIs",
  description:
    "Get up-to-date Razorpay, Zerodha, ONDC, UPI, and 100+ Indian API docs in Claude, Cursor, and VS Code. Free to start.",
};

const LIBRARY_CATEGORIES = [
  {
    title: "Indian Fintech",
    description:
      "Razorpay, Cashfree, Juspay, PayU, Paytm PG, Setu — complete payment integration docs in seconds.",
    color: "text-amber-400",
    border: "border-amber-500/20",
  },
  {
    title: "India Stack / DPI",
    description:
      "ONDC Protocol, UPI/NPCI, Account Aggregator, GSTN, DigiLocker, Bhashini — the hardest APIs to integrate, made accessible.",
    color: "text-green-400",
    border: "border-green-500/20",
  },
  {
    title: "Trading APIs",
    description:
      "Zerodha Kite, Upstox, AngelOne SmartAPI — algo trading and broker integrations with full API coverage.",
    color: "text-blue-400",
    border: "border-blue-500/20",
  },
  {
    title: "Enterprise India",
    description:
      "Zoho CRM, Frappe/ERPNext, Tally Prime, SAP B1 — ERP and enterprise tools Indian businesses actually use.",
    color: "text-purple-400",
    border: "border-purple-500/20",
  },
  {
    title: "Global Frameworks",
    description:
      "React, Next.js, FastAPI, Django, Flutter, Spring Boot — because you're building with these too.",
    color: "text-slate-400",
    border: "border-slate-500/20",
  },
];

const HOW_IT_WORKS = [
  {
    step: "1",
    title: "Get your API key",
    description: "Free at context7india.com/dashboard. No credit card.",
  },
  {
    step: "2",
    title: "Add to your tool",
    description: "One command for Claude, Cursor, or VS Code. Takes 60 seconds.",
  },
  {
    step: "3",
    title: "Just build",
    description: 'Type "use context7india" in any prompt. Accurate docs appear instantly.',
  },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#05080f] text-white">
      {/* Nav */}
      <nav className="border-b border-white/10 px-6 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <div className="font-bold text-[#f59e1c] text-xl">
          context7<span className="text-white">.in</span>
        </div>
        <div className="flex gap-6 text-sm text-gray-400">
          <Link href="/libraries" className="hover:text-white transition-colors">
            Libraries
          </Link>
          <Link href="/docs" className="hover:text-white transition-colors">
            Docs
          </Link>
          <Link href="/pricing" className="hover:text-white transition-colors">
            Pricing
          </Link>
          <Link
            href="https://github.com/context7india/context7-india"
            className="hover:text-white transition-colors"
          >
            GitHub
          </Link>
        </div>
        <Link
          href="/dashboard"
          className="bg-[#f59e1c] text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#fbbf45] transition-colors"
        >
          Get Free API Key
        </Link>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-24 pb-16 text-center">
        <div className="inline-flex items-center gap-2 bg-[#f59e1c]/10 border border-[#f59e1c]/25 text-[#f59e1c] text-xs font-semibold px-4 py-2 rounded-full mb-8 uppercase tracking-wider">
          <span className="w-2 h-2 bg-[#f59e1c] rounded-full animate-pulse" />
          AI-Native · MCP-Compatible · India-First
        </div>
        <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6">
          The Documentation Layer
          <br />
          <span className="text-[#f59e1c]">India&apos;s Developers</span> Deserved
        </h1>
        <p className="text-gray-400 text-xl max-w-2xl mx-auto mb-10">
          Razorpay, Zerodha Kite, ONDC, UPI, GST — instantly in Claude, Cursor, and VS Code. No
          more hallucinated payment flows. No more reading PDFs.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/dashboard"
            className="bg-[#f59e1c] text-black px-8 py-3 rounded-xl font-semibold hover:bg-[#fbbf45] transition-colors"
          >
            Get Free API Key
          </Link>
          <Link
            href="/libraries"
            className="border border-white/20 text-white px-8 py-3 rounded-xl font-semibold hover:bg-white/5 transition-colors"
          >
            See All Libraries →
          </Link>
        </div>
        <p className="text-gray-500 text-sm mt-6">
          Trusted by 500+ Indian developers · 100+ APIs indexed · Hindi docs available
        </p>
      </section>

      {/* Stats */}
      <section className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { val: "100+", label: "Indian APIs indexed" },
            { val: "17M", label: "Developers in India" },
            { val: "Hindi", label: "Regional language docs" },
            { val: "Free", label: "To start" },
          ].map(({ val, label }) => (
            <div
              key={label}
              className="bg-white/5 border border-white/10 rounded-xl p-6 text-center"
            >
              <div className="text-3xl font-bold text-[#f59e1c] mb-1">{val}</div>
              <div className="text-sm text-gray-400">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Problem Section */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
          Your AI assistant doesn&apos;t know Indian APIs.
        </h2>
        <p className="text-gray-400 text-center max-w-2xl mx-auto mb-12">
          Ask Claude to integrate Razorpay and it might reference a deprecated endpoint. Ask Cursor
          about ONDC and watch it hallucinate the Beckn Protocol flow. Context7 indexes 9,000+
          libraries — Indian APIs: zero.
        </p>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              title: "Wrong code, every time",
              body: "Your AI writes Razorpay v2 code when v3 is current. It uses GSTN endpoints that no longer exist. Every integration starts with debugging code that was never right.",
            },
            {
              title: "PDFs shouldn't be documentation",
              body: "UPI specs are PDFs. ONDC has 132 GitHub repos. GSTN has portal-gated docs. Your AI can't read any of it. You can.",
            },
            {
              title: "Hours of context-setting",
              body: "Before every coding session, you paste API docs into your prompt. You repeat yourself every time. The AI forgets by next session.",
            },
          ].map(({ title, body }) => (
            <div
              key={title}
              className="bg-white/5 border border-white/10 rounded-xl p-6"
            >
              <h3 className="text-white font-semibold mb-2">{title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Solution Section */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
          Real docs. Real time. Indian APIs first.
        </h2>
        <p className="text-gray-400 text-center max-w-2xl mx-auto mb-12">
          Context7 India is an MCP server for Indian developers. Type{" "}
          <code className="text-[#f59e1c]">use context7india</code> in Claude or Cursor. Get
          accurate, current documentation injected directly into your AI&apos;s context.
        </p>
        <div className="grid md:grid-cols-2 gap-6">
          {[
            {
              title: "100+ Libraries Indexed",
              body: "Razorpay, Zerodha Kite, ONDC, UPI/NPCI, GSTN, DigiLocker, Zoho, Frappe, Sarvam AI — all the APIs that matter to Indian startups.",
            },
            {
              title: "Hindi Documentation",
              body: "First-ever Hindi developer docs for Indian APIs. Built with Sarvam AI's Mayura model. Tamil, Telugu, and Kannada coming soon.",
            },
            {
              title: "Works Where You Work",
              body: "Claude, Cursor, VS Code, Windsurf — if it supports MCP, it supports Context7 India. One API key, every tool.",
            },
            {
              title: "Always Fresh",
              body: "Automated re-indexing. When Razorpay updates their API, we update our docs. Daily cron runs at 2 AM IST.",
            },
          ].map(({ title, body }) => (
            <div
              key={title}
              className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-6"
            >
              <h3 className="text-white font-semibold mb-2">{title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Library Showcase */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
          Built for how India builds.
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {LIBRARY_CATEGORIES.map(({ title, description, color, border }) => (
            <div
              key={title}
              className={`bg-white/[0.02] border ${border} rounded-xl p-5`}
            >
              <h3 className={`font-semibold mb-2 ${color}`}>{title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
          Three lines. That&apos;s it.
        </h2>
        <p className="text-gray-400 text-center mb-12">
          From zero to real documentation in under a minute.
        </p>
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {HOW_IT_WORKS.map(({ step, title, description }) => (
            <div key={step} className="text-center">
              <div className="w-10 h-10 rounded-full bg-[#f59e1c]/15 border border-[#f59e1c]/30 text-[#f59e1c] font-bold flex items-center justify-center mx-auto mb-4">
                {step}
              </div>
              <h3 className="text-white font-semibold mb-2">{title}</h3>
              <p className="text-gray-400 text-sm">{description}</p>
            </div>
          ))}
        </div>
        {/* Code example */}
        <div className="max-w-3xl mx-auto bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden">
          <div className="px-4 py-2 border-b border-[#1e2d44] text-xs text-gray-500">
            Claude / Cursor prompt
          </div>
          <pre className="p-5 text-sm text-gray-300 font-mono overflow-x-auto leading-relaxed">
            <span className="text-gray-500">User:</span> How do I create a Razorpay payment link?{" "}
            <span className="text-[#f59e1c]">use context7india</span>
            {"\n\n"}
            <span className="text-gray-500">Claude:</span>{" "}
            <span className="text-gray-400 italic">
              [fetching Razorpay documentation via Context7 India...]
            </span>
            {"\n\n"}
            <span className="text-gray-400">
              Based on current Razorpay docs (v1.3, updated 6 hours ago):
            </span>
            {"\n\n"}
            <span className="text-green-300">{`const razorpay = new Razorpay({
  key_id: 'YOUR_KEY',
  key_secret: 'YOUR_SECRET'
});

const paymentLink = await razorpay.paymentLink.create({
  amount: 50000,  // In paise
  currency: 'INR',
  description: 'Payment for Order #1234',
});`}</span>
          </pre>
        </div>
      </section>

      {/* Pricing Preview */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
          Start free. Pay when it saves you money.
        </h2>
        <p className="text-gray-400 text-center mb-12">
          ₹399 is less than 2 samosas a day. Start free, no credit card required.
        </p>
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            {
              name: "Community",
              price: "₹0",
              features: ["100 queries/day", "Top 30 libraries", "English only"],
              highlight: false,
            },
            {
              name: "Pro",
              price: "₹399/mo",
              features: ["Unlimited queries", "All 100+ libraries", "Hindi + regional"],
              highlight: true,
            },
            {
              name: "Team",
              price: "₹999/seat",
              features: ["Everything in Pro", "Unlimited private repos", "SLA 99.9%"],
              highlight: false,
            },
          ].map((plan) => (
            <div
              key={plan.name}
              className={`rounded-xl p-6 text-center ${
                plan.highlight
                  ? "border-2 border-[#f59e1c] bg-[#f59e1c]/[0.04]"
                  : "border border-[#1e2d44] bg-[#0c1120]"
              }`}
            >
              <div className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-2">
                {plan.name}
              </div>
              <div className="text-2xl font-bold mb-4">{plan.price}</div>
              <ul className="text-sm text-gray-400 space-y-2 mb-6">
                {plan.features.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="text-center mt-8">
          <Link
            href="/pricing"
            className="text-[#f59e1c] text-sm hover:underline"
          >
            See full pricing details →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="flex flex-col md:flex-row justify-between items-start gap-8">
            <div>
              <div className="font-bold text-[#f59e1c] text-xl mb-2">
                context7<span className="text-white">.in</span>
              </div>
              <p className="text-gray-500 text-sm max-w-xs">
                Built in India, for India&apos;s developers. The MCP client is Apache 2.0. The
                index is ours.
              </p>
            </div>
            <div className="flex gap-12 text-sm">
              <div className="flex flex-col gap-2 text-gray-400">
                <Link href="/libraries" className="hover:text-white transition-colors">
                  Libraries
                </Link>
                <Link href="/pricing" className="hover:text-white transition-colors">
                  Pricing
                </Link>
                <Link href="/docs" className="hover:text-white transition-colors">
                  Docs
                </Link>
              </div>
              <div className="flex flex-col gap-2 text-gray-400">
                <Link
                  href="https://github.com/context7india/context7-india"
                  className="hover:text-white transition-colors"
                >
                  GitHub
                </Link>
                <Link
                  href="https://twitter.com/context7india"
                  className="hover:text-white transition-colors"
                >
                  Twitter
                </Link>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-white/5 text-center text-xs text-gray-600">
            © 2026 Context7 India. Apache 2.0 (MCP Client). All rights reserved (Index).
          </div>
        </div>
      </footer>
    </main>
  );
}
