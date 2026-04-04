/**
 * MCP Setup Tools Hub — free setup scripts for developers.
 * Zero infra cost. Drives traffic. Solves real pain.
 */
import Link from "next/link";

export const metadata = {
  title: "Free MCP Setup Tools — contextBharat",
  description:
    "One-click setup scripts for GitHub MCP, Context Bharat MCP, and more. Works on macOS, Linux, and Windows. Fix 'spawn npx ENOENT' and org access issues.",
  keywords:
    "mcp setup, github mcp server, spawn npx enoent, claude mcp, cursor mcp, mcp personal access token",
};

const TOOLS = [
  {
    slug: "github-mcp",
    title: "GitHub MCP Setup",
    description:
      "Use GitHub repos, issues, and PRs directly from Claude, Cursor, or VS Code. Guides you through PAT creation with correct permissions.",
    problem: "Org-level access denied? spawn npx ENOENT?",
    badge: "Most Popular",
    badgeColor: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    iconBg: "bg-white/10",
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6 fill-white">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
      </svg>
    ),
    features: [
      "Auto-detects Claude Desktop, Claude Code, Cursor, VS Code",
      "Guides PAT creation with exact permissions needed",
      "Verifies token works before configuring",
      "Fixes 'spawn npx ENOENT' on Windows automatically",
      "Backs up existing config before changes",
    ],
  },
  {
    slug: "#contextbharat",
    title: "Context Bharat MCP Setup",
    description:
      "Get Razorpay, ONDC, Zerodha, UPI docs in your AI editor. Auto-configures for all MCP-compatible tools.",
    problem: "Your AI hallucinates Indian API code?",
    badge: "India-First",
    badgeColor: "bg-green-500/15 text-green-400 border-green-500/30",
    iconBg: "bg-[#f59e1c]/15",
    icon: (
      <span className="text-[#f59e1c] font-bold text-sm">cB</span>
    ),
    features: [
      "Indian API docs always up-to-date",
      "Hindi + 5 regional languages",
      "Free tier — no credit card needed",
      "Works with Claude, Cursor, VS Code, Windsurf",
    ],
  },
  {
    slug: "#coming-soon",
    title: "MCP Doctor",
    description:
      "Diagnoses and fixes the most common MCP issues: ENOENT errors, broken JSON configs, stale tokens, Node.js PATH problems.",
    problem: "MCP server not loading? No error message?",
    badge: "Coming Soon",
    badgeColor: "bg-purple-500/15 text-purple-400 border-purple-500/30",
    iconBg: "bg-purple-500/15",
    icon: (
      <span className="text-purple-400 text-lg">+</span>
    ),
    features: [
      "Validates all MCP config files",
      "Detects Node.js/NVM PATH issues",
      "Tests MCP server connectivity",
      "Checks token validity and permissions",
    ],
  },
  {
    slug: "#coming-soon",
    title: "Multi-Tool Config Sync",
    description:
      "Keep MCP servers in sync across Claude Code, Cursor, VS Code, and Windsurf. Edit once, sync everywhere.",
    problem: "Maintaining 4 separate MCP configs?",
    badge: "Coming Soon",
    badgeColor: "bg-purple-500/15 text-purple-400 border-purple-500/30",
    iconBg: "bg-blue-500/15",
    icon: (
      <span className="text-blue-400 text-lg">&#8644;</span>
    ),
    features: [
      "Detects all installed AI tools",
      "One-command sync across all configs",
      "Handles different config formats per tool",
      "Dry-run mode to preview changes",
    ],
  },
];

export default function ToolsHubPage() {
  return (
    <main className="min-h-screen bg-[#05080f] text-white">
      {/* Nav */}
      <nav className="border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <Link href="/" className="font-bold text-[#f59e1c] text-xl">
            context<span className="text-white">Bharat</span>
          </Link>
          <div className="hidden md:flex gap-6 text-sm text-gray-400">
            <Link href="/docs" className="hover:text-white transition-colors">Install</Link>
            <Link href="/setup" className="text-white">Tools</Link>
            <Link href="/libraries" className="hover:text-white transition-colors">Libraries</Link>
            <Link href="/pricing" className="hover:text-white transition-colors">Plans</Link>
          </div>
          <Link
            href="/dashboard"
            className="bg-[#f59e1c] text-black px-4 py-2 rounded-lg text-sm font-semibold hover:bg-[#fbbf45] transition-colors"
          >
            Get API Key
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="max-w-2xl mb-12">
          <h1 className="text-4xl font-bold mb-4">
            Free Setup Tools for <span className="text-[#f59e1c]">AI Developers</span>
          </h1>
          <p className="text-gray-400 text-lg">
            One-command setup scripts that configure MCP servers on your machine.
            Works on macOS, Linux, and Windows. Everything runs locally — zero data sent to us.
          </p>
        </div>

        {/* OS Support Banner */}
        <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5 mb-10 flex flex-wrap items-center gap-4">
          <span className="text-gray-400 text-sm">Supported platforms:</span>
          <div className="flex gap-3">
            {[
              { os: "macOS", icon: "apple", ext: ".sh" },
              { os: "Linux", icon: "linux", ext: ".sh" },
              { os: "Windows", icon: "windows", ext: ".ps1" },
            ].map(({ os, ext }) => (
              <span
                key={os}
                className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm flex items-center gap-2"
              >
                <span className="text-white font-medium">{os}</span>
                <code className="text-gray-500 text-xs">{ext}</code>
              </span>
            ))}
          </div>
        </div>

        {/* Tools Grid */}
        <div className="grid gap-6">
          {TOOLS.map((tool) => {
            const isLink = tool.slug !== "#contextbharat" && tool.slug !== "#coming-soon";
            const cardClass = `bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden ${isLink ? "hover:border-[#f59e1c]/30 transition-colors cursor-pointer" : "opacity-80"} block`;

            const inner = (
              <div className="p-6 md:p-8">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg ${tool.iconBg} flex items-center justify-center`}>
                      {tool.icon}
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white">{tool.title}</h2>
                      <p className="text-gray-500 text-sm">{tool.problem}</p>
                    </div>
                  </div>
                  <span className={`text-xs font-medium px-2.5 py-1 rounded-full border whitespace-nowrap ${tool.badgeColor}`}>
                    {tool.badge}
                  </span>
                </div>
                <p className="text-gray-400 text-sm mb-5">{tool.description}</p>
                <div className="grid sm:grid-cols-2 gap-2">
                  {tool.features.map((f) => (
                    <div key={f} className="flex items-start gap-2 text-sm text-gray-500">
                      <span className="text-green-400 mt-0.5">&#10003;</span>
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
                {isLink && (
                  <div className="mt-5 pt-5 border-t border-[#1e2d44]">
                    <span className="text-[#f59e1c] text-sm font-medium">
                      View setup guide &rarr;
                    </span>
                  </div>
                )}
              </div>
            );

            if (isLink) {
              return (
                <Link key={tool.title} href={`/setup/${tool.slug}`} className={cardClass}>
                  {inner}
                </Link>
              );
            }

            return (
              <div key={tool.title} className={cardClass}>
                {inner}
              </div>
            );
          })}
        </div>

        {/* Why we built this */}
        <section className="mt-16 max-w-2xl">
          <h2 className="text-2xl font-bold mb-4">Why free setup tools?</h2>
          <div className="text-gray-400 text-sm leading-relaxed space-y-3">
            <p>
              MCP is powerful but setup is painful. The #1 error developers face is
              <code className="text-red-400 mx-1">spawn npx ENOENT</code> — caused by Node.js PATH
              issues that differ across macOS, Linux, and Windows. Org-level PAT restrictions block
              GitHub MCP for most teams. JSON config files silently fail with no error message.
            </p>
            <p>
              These scripts run entirely on your machine. No data is sent to Context Bharat.
              We built them because solving developer pain — even outside our core product —
              is the right thing to do.
            </p>
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="font-bold text-[#f59e1c]">
            context<span className="text-white">Bharat</span>
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            <Link href="/docs" className="hover:text-white transition-colors">Install</Link>
            <Link href="/libraries" className="hover:text-white transition-colors">Libraries</Link>
            <Link href="/pricing" className="hover:text-white transition-colors">Plans</Link>
            <Link href="https://github.com/contextbharat/context-bharat" className="hover:text-white transition-colors">GitHub</Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
