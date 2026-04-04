/**
 * PricingClient — interactive pricing page with monthly/annual toggle,
 * feature comparison table, FAQ accordion, and dynamic library count.
 */
"use client";

import { useState } from "react";
import Link from "next/link";
import { Navbar } from "@/components/navbar";
import { useLibraryCount, formatLibraryCount } from "@/lib/use-library-count";

type Interval = "monthly" | "annual";

interface Plan {
  name: string;
  monthlyPrice: number;
  annualMonthlyPrice: number;
  annualTotalPrice: number;
  per: string;
  highlight: boolean;
  badge?: string;
  features: string[];
  cta: string;
  href: string;
}

const PLANS: Plan[] = [
  {
    name: "Community",
    monthlyPrice: 0,
    annualMonthlyPrice: 0,
    annualTotalPrice: 0,
    per: "Free forever",
    highlight: false,
    features: [
      "100 queries / day",
      "Top 30 libraries",
      "English only",
      "MCP server (local via npx)",
      "Community support",
    ],
    cta: "Get Started Free",
    href: "/login",
  },
  {
    name: "Pro",
    monthlyPrice: 399,
    annualMonthlyPrice: 319,
    annualTotalPrice: 3828,
    per: "per month",
    highlight: true,
    badge: "Most Popular",
    features: [
      "Unlimited queries",
      "All libraries",
      "Hindi + 4 regional languages",
      "Offline documentation packs",
      "Remote MCP (Streamable HTTP)",
      "Private repo indexing (5 repos)",
      "Priority support",
    ],
    cta: "Start Pro",
    href: "/login",
  },
  {
    name: "Team",
    monthlyPrice: 999,
    annualMonthlyPrice: 799,
    annualTotalPrice: 9588,
    per: "per seat / month",
    highlight: false,
    features: [
      "Everything in Pro",
      "Unlimited private repos",
      "Team management dashboard",
      "Usage analytics & insights",
      "SLA 99.9% uptime",
      "Slack / email priority support",
    ],
    cta: "Contact Us",
    href: "mailto:team@contextbharat.com",
  },
];

const FEATURE_COMPARISON = [
  { feature: "Daily queries", free: "100", pro: "Unlimited", team: "Unlimited" },
  { feature: "Libraries accessible", free: "Top 30", pro: "All", team: "All" },
  { feature: "MCP transport", free: "Local (stdio)", pro: "Local + Remote", team: "Local + Remote" },
  { feature: "Hindi + regional docs", free: false, pro: true, team: true },
  { feature: "Offline doc packs", free: false, pro: true, team: true },
  { feature: "Private repo indexing", free: false, pro: "5 repos", team: "Unlimited" },
  { feature: "Team management", free: false, pro: false, team: true },
  { feature: "Usage analytics", free: false, pro: "Basic", team: "Advanced" },
  { feature: "SLA uptime guarantee", free: false, pro: false, team: "99.9%" },
  { feature: "Support", free: "Community", pro: "Priority email", team: "Slack + email" },
  { feature: "API rate limit", free: "100/day", pro: "No limit", team: "No limit" },
  { feature: "Student discount", free: "N/A", pro: "Free", team: "N/A" },
];

const FAQS = [
  {
    q: "Why is it so cheap compared to Context7 ($10/month)?",
    a: "We are built for India. $399 is the right price for Indian developers. We keep costs low with efficient infra on GCP Asia-South + Supabase. No VC-inflated pricing.",
  },
  {
    q: "Can I use it with Claude, Cursor, and VS Code simultaneously?",
    a: "Yes. One API key works across all MCP-compatible tools simultaneously. No per-tool licensing, no device limits.",
  },
  {
    q: "Do you have GitHub Student Pack pricing?",
    a: "Pro is free for verified students. Sign up and apply on your dashboard with your .edu email or GitHub Student Pack.",
  },
  {
    q: "What happens to my data?",
    a: "We only receive the query string your AI sends us. Your code never leaves your machine. We do not log queries beyond rate limiting counters.",
  },
  {
    q: "Can I self-host the MCP server?",
    a: "The MCP client is Apache 2.0 open-source. Run it locally with npx @contextbharat/mcp. The documentation index is hosted by us.",
  },
  {
    q: "Do you support offline usage?",
    a: "Pro tier includes downloadable documentation packs (<5MB per library) for offline use. Perfect for developers in areas with inconsistent connectivity.",
  },
  {
    q: "What is the annual billing discount?",
    a: "Annual plans save you 20%. Pro is $319/mo billed annually ($3,828/year) instead of $399/mo. Team is $799/seat/mo billed annually.",
  },
  {
    q: "Can I switch between monthly and annual?",
    a: "Yes, you can switch at any time. When upgrading to annual, we pro-rate the remaining days on your monthly plan as credit.",
  },
];

function formatINR(amount: number): string {
  if (amount === 0) return "0";
  return amount.toLocaleString("en-IN");
}

export function PricingClient() {
  const [interval, setInterval] = useState<Interval>("monthly");
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const libraryCount = useLibraryCount();

  return (
    <main className="min-h-screen bg-[#05080f] text-white">
      <Navbar />

      <div className="max-w-6xl mx-auto px-6 py-20">
        {/* Header */}
        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 bg-[#f59e1c]/10 border border-[#f59e1c]/20 rounded-full px-4 py-1.5 mb-6">
            <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
            <span className="text-sm text-[#f59e1c] font-medium">
              {formatLibraryCount(libraryCount, "100+")} libraries indexed
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Priced for India. Built to scale.
          </h1>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            Start free, no credit card required. Upgrade when you need unlimited access to every Indian API.
          </p>
        </div>

        {/* Monthly / Annual Toggle */}
        <div className="flex justify-center mb-12">
          <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-1 inline-flex">
            <button
              onClick={() => setInterval("monthly")}
              className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                interval === "monthly"
                  ? "bg-[#f59e1c] text-black"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setInterval("annual")}
              className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                interval === "annual"
                  ? "bg-[#f59e1c] text-black"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Annual
              <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                interval === "annual"
                  ? "bg-black/20 text-black"
                  : "bg-green-500/15 text-green-400"
              }`}>
                -20%
              </span>
            </button>
          </div>
        </div>

        {/* Plan Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-20">
          {PLANS.map((plan) => {
            const price =
              interval === "monthly" ? plan.monthlyPrice : plan.annualMonthlyPrice;
            const showAnnualTotal = interval === "annual" && plan.annualTotalPrice > 0;

            return (
              <div
                key={plan.name}
                className={`rounded-2xl p-7 flex flex-col relative ${
                  plan.highlight
                    ? "border-2 border-[#f59e1c] bg-[#f59e1c]/[0.04] shadow-lg shadow-[#f59e1c]/5"
                    : "border border-[#1e2d44] bg-[#0c1120]"
                }`}
              >
                {plan.badge && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-[#f59e1c] text-black text-xs font-bold px-4 py-1 rounded-full">
                      {plan.badge}
                    </span>
                  </div>
                )}

                <div className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-4 mt-1">
                  {plan.name}
                </div>

                <div className="mb-1 flex items-baseline gap-1">
                  <span className="text-4xl font-bold">
                    {price === 0 ? "Free" : `\u20B9${formatINR(price)}`}
                  </span>
                  {price > 0 && (
                    <span className="text-gray-500 text-sm">/mo</span>
                  )}
                </div>

                {showAnnualTotal ? (
                  <div className="text-gray-500 text-sm mb-6">
                    {`\u20B9${formatINR(plan.annualTotalPrice)} billed annually`}
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm mb-6">{plan.per}</div>
                )}

                {interval === "annual" && plan.monthlyPrice > 0 && (
                  <div className="bg-green-500/10 border border-green-500/20 rounded-lg px-3 py-2 mb-4">
                    <span className="text-green-400 text-xs font-medium">
                      Save {`\u20B9${formatINR((plan.monthlyPrice - plan.annualMonthlyPrice) * 12)}`}/year
                    </span>
                  </div>
                )}

                <ul className="flex flex-col gap-3 mb-8 flex-1">
                  {plan.features.map((f) => (
                    <li key={f} className="flex gap-2.5 text-sm text-gray-300">
                      <svg
                        className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      {f}
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.href}
                  className={`w-full text-center px-4 py-3.5 rounded-xl font-semibold text-sm transition-all ${
                    plan.highlight
                      ? "bg-[#f59e1c] text-black hover:bg-[#fbbf45] hover:shadow-lg hover:shadow-[#f59e1c]/20"
                      : "border border-[#253650] text-white hover:bg-white/5 hover:border-white/20"
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            );
          })}
        </div>

        {/* Feature Comparison Table */}
        <div className="mb-20">
          <h2 className="text-2xl font-bold text-center mb-2">Full feature comparison</h2>
          <p className="text-gray-500 text-center mb-8">
            Every detail, side by side
          </p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#1e2d44]">
                  <th className="text-left py-4 px-4 text-gray-400 text-sm font-medium w-1/4">
                    Feature
                  </th>
                  <th className="text-center py-4 px-4 text-gray-400 text-sm font-medium">
                    Community
                  </th>
                  <th className="text-center py-4 px-4 text-sm font-medium">
                    <span className="text-[#f59e1c]">Pro</span>
                  </th>
                  <th className="text-center py-4 px-4 text-gray-400 text-sm font-medium">
                    Team
                  </th>
                </tr>
              </thead>
              <tbody>
                {FEATURE_COMPARISON.map(({ feature, free, pro, team }, i) => (
                  <tr
                    key={feature}
                    className={`border-b border-[#1e2d44]/50 ${
                      i % 2 === 0 ? "bg-transparent" : "bg-white/[0.01]"
                    }`}
                  >
                    <td className="py-3.5 px-4 text-sm text-gray-300">{feature}</td>
                    <td className="py-3.5 px-4 text-center">
                      <FeatureValue value={free} />
                    </td>
                    <td className="py-3.5 px-4 text-center bg-[#f59e1c]/[0.02]">
                      <FeatureValue value={pro} highlight />
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <FeatureValue value={team} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mb-20">
          <h2 className="text-2xl font-bold text-center mb-2">Frequently asked questions</h2>
          <p className="text-gray-500 text-center mb-10">
            Everything you need to know about our plans
          </p>
          <div className="max-w-3xl mx-auto">
            {FAQS.map(({ q, a }, i) => (
              <div
                key={q}
                className="border-b border-[#1e2d44]/50"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between py-5 text-left group"
                >
                  <span className="text-white text-sm font-medium pr-4 group-hover:text-[#f59e1c] transition-colors">
                    {q}
                  </span>
                  <svg
                    className={`w-5 h-5 text-gray-500 flex-shrink-0 transition-transform ${
                      openFaq === i ? "rotate-180" : ""
                    }`}
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </button>
                {openFaq === i && (
                  <div className="pb-5 text-gray-400 text-sm leading-relaxed">
                    {a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="text-center rounded-2xl bg-gradient-to-b from-[#f59e1c]/5 to-transparent border border-[#f59e1c]/10 px-8 py-16">
          <h3 className="text-2xl font-bold mb-3">
            Ready to stop hallucinating Indian APIs?
          </h3>
          <p className="text-gray-400 mb-8 max-w-lg mx-auto">
            Join developers who ship Indian API integrations faster with accurate, real-time documentation.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/login"
              className="bg-[#f59e1c] text-black px-8 py-3.5 rounded-xl font-semibold hover:bg-[#fbbf45] transition-colors"
            >
              Get Free API Key
            </Link>
            <Link
              href="/libraries"
              className="border border-white/20 text-white px-8 py-3.5 rounded-xl font-semibold hover:bg-white/5 transition-colors"
            >
              Browse Libraries
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}

function FeatureValue({
  value,
  highlight = false,
}: {
  value: boolean | string;
  highlight?: boolean;
}) {
  if (value === true) {
    return (
      <svg
        className={`w-5 h-5 mx-auto ${highlight ? "text-[#f59e1c]" : "text-green-400"}`}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <polyline points="20 6 9 17 4 12" />
      </svg>
    );
  }
  if (value === false) {
    return (
      <svg
        className="w-5 h-5 mx-auto text-gray-700"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      >
        <line x1="5" y1="12" x2="19" y2="12" />
      </svg>
    );
  }
  return (
    <span className={`text-sm ${highlight ? "text-white font-medium" : "text-gray-400"}`}>
      {value}
    </span>
  );
}
