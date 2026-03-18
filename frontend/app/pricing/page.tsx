import Link from "next/link";

export const metadata = {
  title: "Pricing — Context Bharat",
  description: "Free to start. ₹399/month for unlimited access to 100+ Indian APIs.",
};

const plans = [
  {
    name: "Community",
    price: "₹0",
    per: "Free forever",
    highlight: false,
    features: [
      "100 queries / day",
      "Top 30 libraries",
      "English only",
      "MCP server (local)",
      "Community support",
    ],
    na: ["Hindi / regional docs", "Offline packs", "Private repo indexing"],
    cta: "Get Started",
    href: "/login",
  },
  {
    name: "Pro",
    price: "₹399",
    per: "per month (~$4.7)",
    highlight: true,
    badge: "Most Popular",
    features: [
      "Unlimited queries",
      "All 100+ libraries",
      "Hindi + 4 regional languages",
      "Offline documentation packs",
      "Remote MCP (Streamable HTTP)",
      "Private repo indexing (5 repos)",
      "Priority support",
    ],
    na: [],
    cta: "Start Pro",
    href: "/login",
  },
  {
    name: "Team",
    price: "₹999",
    per: "per seat / month",
    highlight: false,
    features: [
      "Everything in Pro",
      "Unlimited private repos",
      "Team management",
      "Usage analytics",
      "SLA 99.9% uptime",
      "Slack / email support",
    ],
    na: [],
    cta: "Contact Us",
    href: "mailto:team@contextbharat.com",
  },
];

const faqs = [
  {
    q: "Why is it so cheap vs Context7 ($10/month)?",
    a: "We're built for India. ₹399 is the right price for Indian developers. We keep costs low with efficient infra on Railway + Supabase.",
  },
  {
    q: "Can I use it with Claude, Cursor, and VS Code simultaneously?",
    a: "Yes — one API key works across all MCP-compatible tools simultaneously. No per-tool licensing.",
  },
  {
    q: "Do you have GitHub Student Pack pricing?",
    a: "Pro is free for verified students. Apply on your dashboard after signing up.",
  },
  {
    q: "What happens to my data?",
    a: "We only receive the query string your AI sends us. Your code never leaves your machine. We don't log queries beyond rate limiting.",
  },
  {
    q: "Can I self-host the MCP server?",
    a: "The MCP client is Apache 2.0 — you can run it locally with npx @contextbharat/mcp. The backend index is hosted by us.",
  },
  {
    q: "Do you support offline usage?",
    a: "Pro tier includes downloadable documentation packs (<5MB per library) for offline use. Perfect for Tier 2/3 city developers.",
  },
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-[#05080f] text-white">
      {/* Nav */}
      <nav className="border-b border-white/10 px-6 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <Link href="/" className="font-bold text-[#f59e1c] text-xl">
          contextbharat<span className="text-white">.com</span>
        </Link>
        <div className="flex gap-6 text-sm text-gray-400">
          <Link href="/libraries" className="hover:text-white transition-colors">
            Libraries
          </Link>
          <Link href="/pricing" className="text-white">
            Pricing
          </Link>
        </div>
        <Link
          href="/dashboard"
          className="bg-[#f59e1c] text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#fbbf45] transition-colors"
        >
          Get Free API Key
        </Link>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-20">
        {/* Header */}
        <div className="text-center mb-14">
          <h1 className="text-4xl font-bold mb-4">Price for India. Scale to the world.</h1>
          <p className="text-gray-400 text-lg">
            ₹399 is less than 2 samosas a day. Start free, no credit card required.
          </p>
        </div>

        {/* Plans */}
        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl p-7 flex flex-col ${
                plan.highlight
                  ? "border-2 border-[#f59e1c] bg-[#f59e1c]/[0.04]"
                  : "border border-[#1e2d44] bg-[#0c1120]"
              }`}
            >
              {plan.badge && (
                <div className="inline-block bg-[#f59e1c] text-black text-xs font-bold px-3 py-1 rounded mb-3 self-start">
                  {plan.badge}
                </div>
              )}
              <div className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-2">
                {plan.name}
              </div>
              <div className="text-3xl font-bold mb-1">{plan.price}</div>
              <div className="text-gray-500 text-sm mb-6">{plan.per}</div>

              <ul className="flex flex-col gap-2.5 mb-6 flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex gap-2 text-sm text-gray-300">
                    <span className="text-green-400 mt-0.5">&#10003;</span> {f}
                  </li>
                ))}
                {plan.na.map((f) => (
                  <li key={f} className="flex gap-2 text-sm text-gray-600">
                    <span className="mt-0.5">&ndash;</span> {f}
                  </li>
                ))}
              </ul>

              <Link
                href={plan.href}
                className={`w-full text-center px-4 py-3 rounded-xl font-semibold text-sm transition-colors ${
                  plan.highlight
                    ? "bg-[#f59e1c] text-black hover:bg-[#fbbf45]"
                    : "border border-[#253650] text-white hover:bg-white/5"
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-20">
          <h2 className="text-2xl font-bold text-center mb-10">Frequently Asked Questions</h2>
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {faqs.map(({ q, a }) => (
              <div key={q} className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
                <div className="text-white font-medium text-sm mb-2">{q}</div>
                <div className="text-gray-400 text-sm leading-relaxed">{a}</div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="mt-20 text-center">
          <h3 className="text-xl font-bold mb-4">Ready to stop hallucinating Indian APIs?</h3>
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
              Browse Libraries
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
