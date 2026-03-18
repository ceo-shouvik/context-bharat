/**
 * Docs / Setup page — how to connect Context Bharat MCP to your AI tools.
 */
import Link from "next/link";

export const metadata = {
  title: "Setup Guide — contextBharat",
  description:
    "Connect Context Bharat MCP to Claude, Cursor, VS Code, and Windsurf in under 60 seconds.",
};

const SETUP_OPTIONS = [
  {
    tool: "Claude Desktop",
    icon: "C",
    iconBg: "bg-orange-500/15 text-orange-400",
    config: `{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp"]
    }
  }
}`,
    configPath: "~/.claude.json",
    steps: [
      "Open Claude Desktop settings",
      "Navigate to MCP Servers section",
      "Add the configuration below",
      'Restart Claude and type "use contextbharat" in any prompt',
    ],
  },
  {
    tool: "Cursor",
    icon: "⌘",
    iconBg: "bg-blue-500/15 text-blue-400",
    config: `{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp"]
    }
  }
}`,
    configPath: ".cursor/mcp.json",
    steps: [
      "Open Cursor Settings → MCP",
      "Click 'Add new MCP server'",
      "Paste the configuration below",
      'Type "use contextbharat" in Cursor chat',
    ],
  },
  {
    tool: "VS Code (Copilot)",
    icon: "VS",
    iconBg: "bg-purple-500/15 text-purple-400",
    config: `{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp"]
    }
  }
}`,
    configPath: ".vscode/mcp.json",
    steps: [
      "Create .vscode/mcp.json in your project root",
      "Paste the configuration below",
      "Enable MCP in VS Code settings",
      'Use "use contextbharat" in Copilot chat',
    ],
  },
  {
    tool: "Windsurf",
    icon: "W",
    iconBg: "bg-teal-500/15 text-teal-400",
    config: `{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp"]
    }
  }
}`,
    configPath: "~/.codeium/windsurf/mcp_config.json",
    steps: [
      "Open Windsurf Settings → MCP",
      "Add a new MCP server",
      "Paste the configuration below",
      'Type "use contextbharat" in Cascade',
    ],
  },
];

const API_EXAMPLES = [
  {
    title: "Resolve Library ID",
    method: "POST",
    endpoint: "/v1/libraries/resolve",
    body: `{
  "query": "razorpay payment integration",
  "library_name": "razorpay"
}`,
    response: `{
  "library_id": "/razorpay/razorpay-sdk",
  "name": "Razorpay",
  "confidence": 0.98
}`,
  },
  {
    title: "Query Documentation",
    method: "POST",
    endpoint: "/v1/docs/query",
    body: `{
  "library_id": "/razorpay/razorpay-sdk",
  "query": "create payment link",
  "token_budget": 5000,
  "language": "en"
}`,
    response: `{
  "docs": "## Create a Payment Link\\n\\nUse POST /payment_links...",
  "sources": ["https://razorpay.com/docs/..."],
  "freshness_score": 0.97
}`,
  },
];

export default function DocsPage() {
  return (
    <main className="min-h-screen bg-[#05080f] text-white">
      {/* Nav */}
      <nav className="border-b border-white/10 px-6 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <Link href="/" className="font-bold text-[#f59e1c] text-xl">
          context<span className="text-white">Bharat</span>
        </Link>
        <div className="flex gap-6 text-sm text-gray-400">
          <Link href="/libraries" className="hover:text-white transition-colors">
            Libraries
          </Link>
          <Link href="/docs" className="text-white">
            Docs
          </Link>
          <Link href="/pricing" className="hover:text-white transition-colors">
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

      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <h1 className="text-4xl font-bold mb-4">Get Started</h1>
        <p className="text-gray-400 text-lg mb-12">
          Connect Context Bharat to your AI coding assistant in under 60 seconds. No API key
          required for the free tier (100 queries/day).
        </p>

        {/* Quick Install */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">Quick Install</h2>
          <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-6">
            <p className="text-gray-400 text-sm mb-3">
              Works with any MCP-compatible tool. Just run:
            </p>
            <pre className="bg-black/40 rounded-lg p-4 text-green-300 font-mono text-sm">
              npx @contextbharat/mcp
            </pre>
            <p className="text-gray-500 text-xs mt-3">
              Or with an API key for higher limits:{" "}
              <code className="text-gray-400">npx @contextbharat/mcp --api-key YOUR_KEY</code>
            </p>
          </div>
        </section>

        {/* Tool-specific setup */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">Setup by Tool</h2>
          <div className="grid gap-6">
            {SETUP_OPTIONS.map((opt) => (
              <div
                key={opt.tool}
                className="bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden"
              >
                <div className="px-6 py-4 border-b border-[#1e2d44] flex items-center gap-3">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${opt.iconBg}`}
                  >
                    {opt.icon}
                  </div>
                  <div>
                    <div className="text-white font-semibold">{opt.tool}</div>
                    <div className="text-gray-500 text-xs font-mono">{opt.configPath}</div>
                  </div>
                </div>
                <div className="p-6">
                  <ol className="list-decimal list-inside text-sm text-gray-400 space-y-2 mb-4">
                    {opt.steps.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ol>
                  <pre className="bg-black/40 rounded-lg p-4 text-green-300 font-mono text-xs overflow-x-auto">
                    {opt.config}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Remote MCP (Pro) */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">Remote MCP Server (Pro)</h2>
          <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-6">
            <p className="text-gray-400 text-sm mb-4">
              Pro users can use the remote server — no local npx needed. Lower latency, always
              up-to-date.
            </p>
            <pre className="bg-black/40 rounded-lg p-4 text-green-300 font-mono text-xs overflow-x-auto">
              {`{
  "mcpServers": {
    "contextbharat": {
      "url": "https://mcp.contextbharat.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}`}
            </pre>
          </div>
        </section>

        {/* MCP Tools */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">MCP Tools</h2>
          <p className="text-gray-400 text-sm mb-6">
            Context Bharat exposes two MCP tools that your AI assistant calls automatically:
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
              <div className="text-[#f59e1c] font-mono text-sm font-bold mb-2">
                resolve-library-id
              </div>
              <p className="text-gray-400 text-sm">
                Maps a library name (e.g., &quot;razorpay&quot;) to its canonical ID
                (/razorpay/razorpay-sdk). Supports fuzzy matching and tag-based search.
              </p>
            </div>
            <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
              <div className="text-[#f59e1c] font-mono text-sm font-bold mb-2">query-docs</div>
              <p className="text-gray-400 text-sm">
                Retrieves relevant documentation chunks within a token budget. Supports 6 languages
                (English, Hindi, Tamil, Telugu, Kannada, Bengali).
              </p>
            </div>
          </div>
        </section>

        {/* REST API */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">REST API</h2>
          <p className="text-gray-400 text-sm mb-6">
            You can also call the API directly from your applications. Base URL:{" "}
            <code className="text-[#f59e1c]">https://api.contextbharat.com</code>
          </p>
          <div className="grid gap-6">
            {API_EXAMPLES.map((ex) => (
              <div
                key={ex.title}
                className="bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden"
              >
                <div className="px-5 py-3 border-b border-[#1e2d44] flex items-center gap-3">
                  <span className="bg-green-500/15 text-green-400 text-xs font-bold px-2 py-0.5 rounded">
                    {ex.method}
                  </span>
                  <span className="text-white font-mono text-sm">{ex.endpoint}</span>
                  <span className="text-gray-500 text-xs ml-auto">{ex.title}</span>
                </div>
                <div className="grid md:grid-cols-2 divide-x divide-[#1e2d44]">
                  <div className="p-4">
                    <div className="text-gray-500 text-xs mb-2">Request</div>
                    <pre className="text-gray-300 font-mono text-xs">{ex.body}</pre>
                  </div>
                  <div className="p-4">
                    <div className="text-gray-500 text-xs mb-2">Response</div>
                    <pre className="text-green-300 font-mono text-xs">{ex.response}</pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Languages */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">Supported Languages</h2>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
            {[
              { code: "en", name: "English", flag: "🇬🇧" },
              { code: "hi", name: "Hindi", flag: "🇮🇳" },
              { code: "ta", name: "Tamil", flag: "🇮🇳" },
              { code: "te", name: "Telugu", flag: "🇮🇳" },
              { code: "kn", name: "Kannada", flag: "🇮🇳" },
              { code: "bn", name: "Bengali", flag: "🇮🇳" },
            ].map(({ code, name, flag }) => (
              <div
                key={code}
                className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-4 text-center"
              >
                <div className="text-2xl mb-1">{flag}</div>
                <div className="text-white text-sm font-medium">{name}</div>
                <div className="text-gray-500 text-xs font-mono">{code}</div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <div className="text-center mt-12 py-12 border-t border-white/10">
          <h3 className="text-xl font-bold mb-4">Ready to start?</h3>
          <div className="flex gap-4 justify-center">
            <Link
              href="/dashboard"
              className="bg-[#f59e1c] text-black px-6 py-3 rounded-xl font-semibold hover:bg-[#fbbf45] transition-colors"
            >
              Get Free API Key
            </Link>
            <Link
              href="/libraries"
              className="border border-white/20 text-white px-6 py-3 rounded-xl font-semibold hover:bg-white/5 transition-colors"
            >
              Browse Libraries
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
