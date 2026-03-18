/**
 * Landing page — contextBharat
 * UX: Demo-first. Show value before asking for signup.
 */
import Link from "next/link";
import { LivePlayground } from "@/components/live-playground";
import { LogoSlider } from "@/components/logo-slider";

export const metadata = {
  title: "contextBharat — Up-to-date docs for Indian APIs in your AI editor",
  description:
    "Get up-to-date Razorpay, Zerodha, ONDC, UPI, and 100+ Indian API docs in Claude, Cursor, and VS Code. Free MCP server.",
};

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#05080f] text-white">
      {/* Nav — simplified */}
      <nav className="border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <Link href="/" className="font-bold text-[#f59e1c] text-xl">
            context<span className="text-white">Bharat</span>
          </Link>
          <div className="hidden md:flex gap-6 text-sm text-gray-400">
            <Link href="/docs" className="hover:text-white transition-colors">Install</Link>
            <Link href="/libraries" className="hover:text-white transition-colors">Libraries</Link>
            <Link href="/pricing" className="hover:text-white transition-colors">Plans</Link>
          </div>
          <div className="flex gap-3">
            <Link
              href="#try"
              className="bg-[#f59e1c] text-black px-4 py-2 rounded-lg text-sm font-semibold hover:bg-[#fbbf45] transition-colors"
            >
              Try Live
            </Link>
            <Link
              href="/dashboard"
              className="border border-white/20 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors hidden md:block"
            >
              Get API Key
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero — clear, concise */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-12 text-center">
        <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-5">
          Up-to-date docs for <span className="text-[#f59e1c]">Indian APIs</span>
          <br className="hidden md:block" /> in your AI editor
        </h1>
        <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto mb-8">
          Razorpay, ONDC, UPI, Zerodha, GSTN — accurate documentation injected into
          Claude, Cursor, and VS Code via MCP. No hallucinations. Always fresh.
        </p>
        <div className="flex gap-3 justify-center mb-4">
          <Link
            href="#try"
            className="bg-[#f59e1c] text-black px-8 py-3 rounded-xl font-semibold hover:bg-[#fbbf45] transition-colors"
          >
            Try It Now — Free
          </Link>
          <Link
            href="/docs"
            className="border border-white/20 text-white px-8 py-3 rounded-xl font-semibold hover:bg-white/5 transition-colors"
          >
            Install in 60s
          </Link>
        </div>
        <p className="text-gray-600 text-sm">
          No signup required to try. 100+ libraries indexed. Hindi docs available.
        </p>
      </section>

      {/* Install snippet — immediate clarity */}
      <section className="max-w-3xl mx-auto px-6 pb-12">
        <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-gray-500 text-xs">Add to Claude / Cursor / VS Code</span>
            <span className="text-green-400 text-xs flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
              MCP Compatible
            </span>
          </div>
          <pre className="bg-black/40 rounded-lg p-4 text-sm text-green-300 font-mono overflow-x-auto">
{`{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp"]
    }
  }
}`}
          </pre>
          <p className="text-gray-500 text-xs mt-3">
            Then type <code className="text-[#f59e1c] font-semibold">use contextbharat</code> in
            any prompt. That&apos;s it.
          </p>
        </div>
      </section>

      {/* Logo slider — social proof */}
      <LogoSlider />

      {/* Live Playground — the hero feature */}
      <section id="try" className="max-w-4xl mx-auto px-6 py-16">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-3">Try it right now</h2>
          <p className="text-gray-400">
            This is exactly what your AI assistant receives. Pick a library, ask a question.
          </p>
        </div>
        <LivePlayground />
      </section>

      {/* What it does — 3 clear benefits */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: "01",
              title: "Your AI knows Indian APIs",
              body: "Stop pasting docs into prompts. contextBharat gives Claude and Cursor real-time access to Razorpay, ONDC, UPI, Zerodha, GSTN, and 100+ more libraries.",
            },
            {
              icon: "02",
              title: "Always up-to-date",
              body: "We re-crawl every library daily. When Razorpay ships a new API version, your AI knows about it within 24 hours. No more deprecated code.",
            },
            {
              icon: "03",
              title: "Hindi + regional languages",
              body: "First-ever Hindi developer docs for Indian APIs. Tamil, Telugu, Kannada, Bengali also supported. Built with Sarvam AI Mayura.",
            },
          ].map(({ icon, title, body }) => (
            <div key={icon}>
              <div className="text-[#f59e1c] font-mono text-sm font-bold mb-3">{icon}</div>
              <h3 className="text-white font-semibold text-lg mb-2">{title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Library categories */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold">100+ Libraries Indexed</h2>
          <Link href="/libraries" className="text-[#f59e1c] text-sm hover:underline">
            Browse all →
          </Link>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { title: "Indian Fintech", libs: "Razorpay, Cashfree, Juspay, Setu, PayU", color: "text-amber-400", border: "border-amber-500/20" },
            { title: "India Stack / DPI", libs: "ONDC, UPI/NPCI, GSTN, DigiLocker, Bhashini, AA", color: "text-green-400", border: "border-green-500/20" },
            { title: "Trading APIs", libs: "Zerodha Kite, Upstox, AngelOne SmartAPI", color: "text-blue-400", border: "border-blue-500/20" },
            { title: "Enterprise", libs: "Zoho CRM, Frappe/ERPNext, Tally Prime", color: "text-purple-400", border: "border-purple-500/20" },
            { title: "Indian AI", libs: "Sarvam AI, Krutrim, AI4Bharat, Bhashini", color: "text-pink-400", border: "border-pink-500/20" },
            { title: "Global Frameworks", libs: "React, Next.js, FastAPI, Django, Flutter", color: "text-slate-400", border: "border-slate-500/20" },
          ].map(({ title, libs, color, border }) => (
            <div key={title} className={`bg-white/[0.02] border ${border} rounded-xl p-5`}>
              <h3 className={`font-semibold mb-1 ${color}`}>{title}</h3>
              <p className="text-gray-500 text-sm">{libs}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works — visual flow */}
      <section className="max-w-4xl mx-auto px-6 py-20">
        <h2 className="text-2xl font-bold text-center mb-12">How it works</h2>
        <div className="relative">
          {/* Connection line */}
          <div className="hidden md:block absolute top-8 left-[16.5%] right-[16.5%] h-px bg-gradient-to-r from-[#f59e1c]/0 via-[#f59e1c]/30 to-[#f59e1c]/0" />
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Install MCP", desc: "One JSON config. Works with Claude, Cursor, VS Code, Windsurf.", cta: "See install guide", href: "/docs" },
              { step: "2", title: "Ask your question", desc: "Type naturally. Mention the library or say \"use contextbharat\".", cta: null, href: null },
              { step: "3", title: "Get real docs", desc: "Your AI receives verified, up-to-date documentation with code examples.", cta: "Try it now", href: "#try" },
            ].map(({ step, title, desc, cta, href }) => (
              <div key={step} className="text-center">
                <div className="w-12 h-12 rounded-full bg-[#f59e1c]/15 border border-[#f59e1c]/30 text-[#f59e1c] font-bold text-lg flex items-center justify-center mx-auto mb-4">
                  {step}
                </div>
                <h3 className="text-white font-semibold mb-2">{title}</h3>
                <p className="text-gray-400 text-sm mb-3">{desc}</p>
                {cta && href && (
                  <Link href={href} className="text-[#f59e1c] text-xs hover:underline">
                    {cta} →
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social proof */}
      <section className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { val: "100+", label: "Libraries indexed" },
            { val: "<2s", label: "Response latency" },
            { val: "6", label: "Languages supported" },
            { val: "Free", label: "No credit card" },
          ].map(({ val, label }) => (
            <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-5 text-center">
              <div className="text-2xl font-bold text-[#f59e1c] mb-1">{val}</div>
              <div className="text-sm text-gray-500">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing preview */}
      <section className="max-w-4xl mx-auto px-6 py-20">
        <h2 className="text-2xl font-bold text-center mb-2">Simple pricing</h2>
        <p className="text-gray-400 text-center mb-10">Start free. Upgrade when you need more.</p>
        <div className="grid md:grid-cols-3 gap-5">
          {[
            { name: "Free", price: "₹0", desc: "100 queries/day, 30 libraries", hl: false },
            { name: "Pro", price: "₹399/mo", desc: "Unlimited, all libraries, Hindi", hl: true },
            { name: "Team", price: "₹999/seat", desc: "Private repos, SLA, analytics", hl: false },
          ].map((p) => (
            <div key={p.name} className={`rounded-xl p-5 text-center ${p.hl ? "border-2 border-[#f59e1c] bg-[#f59e1c]/[0.04]" : "border border-[#1e2d44] bg-[#0c1120]"}`}>
              <div className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-1">{p.name}</div>
              <div className="text-2xl font-bold mb-1">{p.price}</div>
              <div className="text-gray-500 text-sm">{p.desc}</div>
            </div>
          ))}
        </div>
        <div className="text-center mt-6">
          <Link href="/pricing" className="text-[#f59e1c] text-sm hover:underline">
            Compare plans →
          </Link>
        </div>
      </section>

      {/* Final CTA */}
      <section className="max-w-3xl mx-auto px-6 py-20 text-center">
        <h2 className="text-3xl font-bold mb-4">Stop hallucinating Indian APIs</h2>
        <p className="text-gray-400 mb-8">
          Add contextBharat to your editor in 60 seconds. Free forever for individuals.
        </p>
        <div className="flex gap-3 justify-center">
          <Link
            href="/docs"
            className="bg-[#f59e1c] text-black px-8 py-3 rounded-xl font-semibold hover:bg-[#fbbf45] transition-colors"
          >
            Install Now
          </Link>
          <Link
            href="#try"
            className="border border-white/20 text-white px-8 py-3 rounded-xl font-semibold hover:bg-white/5 transition-colors"
          >
            Try Live Demo
          </Link>
        </div>
      </section>

      {/* Footer — clean */}
      <footer className="border-t border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-10">
          <div className="flex flex-col md:flex-row justify-between items-start gap-8">
            <div>
              <div className="font-bold text-[#f59e1c] text-lg mb-1">
                context<span className="text-white">Bharat</span>
              </div>
              <p className="text-gray-600 text-sm max-w-xs">
                Up-to-date Indian API docs for AI editors. Open-source MCP client.
              </p>
            </div>
            <div className="flex gap-10 text-sm text-gray-500">
              <div className="flex flex-col gap-2">
                <Link href="/docs" className="hover:text-white transition-colors">Install</Link>
                <Link href="/libraries" className="hover:text-white transition-colors">Libraries</Link>
                <Link href="/pricing" className="hover:text-white transition-colors">Plans</Link>
              </div>
              <div className="flex flex-col gap-2">
                <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
                <Link href="https://github.com/contextbharat/context-bharat" className="hover:text-white transition-colors">GitHub</Link>
                <Link href="https://twitter.com/contextbharat" className="hover:text-white transition-colors">Twitter</Link>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-5 border-t border-white/5 text-center text-xs text-gray-700">
            Built in India. Apache 2.0 (MCP Client). © 2026 contextBharat.
          </div>
        </div>
      </footer>
    </main>
  );
}
