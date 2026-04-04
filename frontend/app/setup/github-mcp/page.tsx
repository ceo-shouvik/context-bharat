/**
 * GitHub MCP Setup — detailed guide with OS-specific instructions.
 * Client component for OS detection + tab switching.
 */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Navbar } from "@/components/navbar";

type OS = "macos" | "linux" | "windows";

function detectOS(): OS {
  if (typeof navigator === "undefined") return "linux";
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes("win")) return "windows";
  if (ua.includes("mac")) return "macos";
  return "linux";
}

/* ─── Config snippets per OS ────────────────────────────────────────────── */

const INSTALL_COMMAND: Record<OS, { label: string; cmd: string }> = {
  macos: {
    label: "Terminal (macOS)",
    cmd: "curl -fsSL https://contextbharat.com/setup/github-mcp.sh | bash",
  },
  linux: {
    label: "Terminal (Linux)",
    cmd: "curl -fsSL https://contextbharat.com/setup/github-mcp.sh | bash",
  },
  windows: {
    label: "PowerShell (Windows)",
    cmd: 'powershell -ExecutionPolicy Bypass -Command "irm https://contextbharat.com/setup/github-mcp.ps1 | iex"',
  },
};

const MCP_CONFIG: Record<OS, string> = {
  macos: `{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_TOKEN_HERE"
      }
    }
  }
}`,
  linux: `{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_TOKEN_HERE"
      }
    }
  }
}`,
  windows: `{
  "mcpServers": {
    "github": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_TOKEN_HERE"
      }
    }
  }
}`,
};

const CONFIG_PATHS: Record<OS, { tool: string; path: string; icon: string; iconBg: string }[]> = {
  macos: [
    { tool: "Claude Desktop", path: "~/Library/Application Support/Claude/claude_desktop_config.json", icon: "C", iconBg: "bg-orange-500/15 text-orange-400" },
    { tool: "Claude Code", path: "~/.claude.json", icon: "CC", iconBg: "bg-orange-500/15 text-orange-300" },
    { tool: "Cursor", path: "~/.cursor/mcp.json", icon: "Cu", iconBg: "bg-blue-500/15 text-blue-400" },
    { tool: "VS Code", path: ".vscode/mcp.json (project root)", icon: "VS", iconBg: "bg-purple-500/15 text-purple-400" },
    { tool: "Windsurf", path: "~/.codeium/windsurf/mcp_config.json", icon: "W", iconBg: "bg-teal-500/15 text-teal-400" },
  ],
  linux: [
    { tool: "Claude Desktop", path: "~/.config/Claude/claude_desktop_config.json", icon: "C", iconBg: "bg-orange-500/15 text-orange-400" },
    { tool: "Claude Code", path: "~/.claude.json", icon: "CC", iconBg: "bg-orange-500/15 text-orange-300" },
    { tool: "Cursor", path: "~/.cursor/mcp.json", icon: "Cu", iconBg: "bg-blue-500/15 text-blue-400" },
    { tool: "VS Code", path: ".vscode/mcp.json (project root)", icon: "VS", iconBg: "bg-purple-500/15 text-purple-400" },
    { tool: "Windsurf", path: "~/.codeium/windsurf/mcp_config.json", icon: "W", iconBg: "bg-teal-500/15 text-teal-400" },
  ],
  windows: [
    { tool: "Claude Desktop", path: "%APPDATA%\\Claude\\claude_desktop_config.json", icon: "C", iconBg: "bg-orange-500/15 text-orange-400" },
    { tool: "Claude Code", path: "%USERPROFILE%\\.claude.json", icon: "CC", iconBg: "bg-orange-500/15 text-orange-300" },
    { tool: "Cursor", path: "%USERPROFILE%\\.cursor\\mcp.json", icon: "Cu", iconBg: "bg-blue-500/15 text-blue-400" },
    { tool: "VS Code", path: ".vscode\\mcp.json (project root)", icon: "VS", iconBg: "bg-purple-500/15 text-purple-400" },
    { tool: "Windsurf", path: "%USERPROFILE%\\.codeium\\windsurf\\mcp_config.json", icon: "W", iconBg: "bg-teal-500/15 text-teal-400" },
  ],
};

const OS_LABELS: Record<OS, string> = {
  macos: "macOS",
  linux: "Linux",
  windows: "Windows",
};

/* ─── Copy button ────────────────────────────────────────────────────────── */

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="text-xs text-gray-500 hover:text-white transition-colors px-2 py-1 rounded border border-white/10 hover:border-white/20"
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}

/* ─── OS Tab Selector ────────────────────────────────────────────────────── */

function OSTabs({ os, setOs }: { os: OS; setOs: (o: OS) => void }) {
  return (
    <div className="flex gap-1 bg-[#0c1120] border border-[#1e2d44] rounded-lg p-1 w-fit">
      {(["macos", "linux", "windows"] as OS[]).map((o) => (
        <button
          key={o}
          onClick={() => setOs(o)}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            os === o
              ? "bg-[#f59e1c] text-black"
              : "text-gray-400 hover:text-white"
          }`}
        >
          {OS_LABELS[o]}
        </button>
      ))}
    </div>
  );
}

/* ─── Main Page ──────────────────────────────────────────────────────────── */

export default function GitHubMcpPage() {
  const [os, setOs] = useState<OS>("linux");
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    setOs(detectOS());
  }, []);

  const copyText = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <main className="min-h-screen bg-[#05080f] text-white">
      <Navbar />

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Breadcrumb */}
        <div className="text-sm text-gray-500 mb-8">
          <Link href="/setup" className="hover:text-white transition-colors">Tools</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-300">GitHub MCP Setup</span>
        </div>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-3">
            Set Up GitHub MCP Server
          </h1>
          <p className="text-gray-400 text-lg">
            Access GitHub repos, issues, and PRs from Claude, Cursor, or VS Code.
            Guided setup with automatic configuration — takes 2 minutes.
          </p>
        </div>

        {/* OS Selector */}
        <div className="mb-8 flex items-center gap-4">
          <span className="text-gray-500 text-sm">Your OS:</span>
          <OSTabs os={os} setOs={setOs} />
        </div>

        {/* Quick Install (automated) */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Quick Install (Automated)</h2>
          <p className="text-gray-400 text-sm mb-4">
            Our script guides you through PAT creation, verifies it works, and configures your AI tools automatically.
          </p>
          <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-5 py-3 border-b border-[#1e2d44]">
              <span className="text-gray-500 text-xs">{INSTALL_COMMAND[os].label}</span>
              <CopyButton text={INSTALL_COMMAND[os].cmd} />
            </div>
            <pre className="p-5 text-green-300 font-mono text-sm overflow-x-auto">
              {INSTALL_COMMAND[os].cmd}
            </pre>
          </div>

          {os === "windows" && (
            <div className="mt-3 bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 text-sm">
              <span className="text-amber-400 font-medium">Windows note:</span>
              <span className="text-gray-400 ml-2">
                This script uses <code className="text-amber-300">cmd /c npx</code> instead of bare <code className="text-amber-300">npx</code>,
                which fixes the common <code className="text-red-400">spawn npx ENOENT</code> error on Windows.
              </span>
            </div>
          )}

          <div className="mt-4 text-gray-500 text-xs">
            Or clone and run locally:
            <code className="text-gray-400 ml-2">
              {os === "windows"
                ? "powershell -ExecutionPolicy Bypass -File tools\\setup-github-mcp.ps1"
                : "bash tools/setup-github-mcp.sh"}
            </code>
          </div>
        </section>

        {/* Manual Setup */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Manual Setup</h2>

          {/* Step 1: Create PAT */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-3">
              <span className="w-7 h-7 rounded-full bg-[#f59e1c]/15 border border-[#f59e1c]/30 text-[#f59e1c] text-xs font-bold flex items-center justify-center">1</span>
              Create a Fine-Grained PAT
            </h3>
            <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
              <ol className="list-decimal list-inside text-sm text-gray-400 space-y-3">
                <li>
                  Go to{" "}
                  <a
                    href="https://github.com/settings/tokens?type=beta"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#f59e1c] hover:underline"
                  >
                    github.com/settings/tokens
                  </a>{" "}
                  (Fine-grained tokens)
                </li>
                <li>Click <span className="text-white font-medium">Generate new token</span></li>
                <li>
                  Set token name to <code className="text-gray-300">MCP Server</code>, expiration to <code className="text-gray-300">90 days</code>
                </li>
                <li>
                  Repository access: <span className="text-white">All repositories</span> (or select specific ones)
                </li>
                <li>
                  Set these permissions under &quot;Repository permissions&quot;:
                </li>
              </ol>

              <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { perm: "Contents", level: "Read-only", desc: "Read code & files" },
                  { perm: "Issues", level: "Read & Write", desc: "View & create issues" },
                  { perm: "Pull requests", level: "Read & Write", desc: "View & create PRs" },
                  { perm: "Metadata", level: "Read-only", desc: "Auto-selected" },
                ].map(({ perm, level, desc }) => (
                  <div key={perm} className="bg-black/30 rounded-lg p-3">
                    <div className="text-white text-xs font-medium">{perm}</div>
                    <div className="text-green-400 text-xs">{level}</div>
                    <div className="text-gray-600 text-[10px] mt-0.5">{desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Step 2: Add config */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-3">
              <span className="w-7 h-7 rounded-full bg-[#f59e1c]/15 border border-[#f59e1c]/30 text-[#f59e1c] text-xs font-bold flex items-center justify-center">2</span>
              Add to your AI tool
            </h3>

            <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-5 py-3 border-b border-[#1e2d44]">
                <span className="text-gray-500 text-xs">
                  MCP config for {OS_LABELS[os]}
                </span>
                <CopyButton text={MCP_CONFIG[os]} />
              </div>
              <pre className="p-5 text-green-300 font-mono text-xs overflow-x-auto">
                {MCP_CONFIG[os]}
              </pre>
            </div>

            {os === "windows" && (
              <div className="mt-3 bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 text-sm text-gray-400">
                <span className="text-blue-400 font-medium">Why <code>cmd /c npx</code>?</span>{" "}
                On Windows, MCP clients often can&apos;t find <code>npx</code> directly because GUI apps
                don&apos;t inherit the same PATH as your terminal. Wrapping with <code>cmd /c</code> resolves
                the <code className="text-red-400">spawn npx ENOENT</code> error.
              </div>
            )}

            {/* Config file paths */}
            <div className="mt-5">
              <p className="text-gray-500 text-sm mb-3">Paste the config into the right file for your tool:</p>
              <div className="grid gap-2">
                {CONFIG_PATHS[os].map(({ tool, path, icon, iconBg }) => (
                  <div key={tool} className="flex items-center gap-3 bg-[#0c1120] border border-[#1e2d44] rounded-lg px-4 py-3">
                    <div className={`w-7 h-7 rounded flex items-center justify-center text-[10px] font-bold ${iconBg}`}>
                      {icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-white text-sm font-medium">{tool}</div>
                      <div className="text-gray-500 text-xs font-mono truncate">{path}</div>
                    </div>
                    <button
                      onClick={() => copyText(tool, path)}
                      className="text-xs text-gray-600 hover:text-white transition-colors shrink-0"
                    >
                      {copied === tool ? "Copied!" : "Copy path"}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Step 3: Restart */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-3">
              <span className="w-7 h-7 rounded-full bg-[#f59e1c]/15 border border-[#f59e1c]/30 text-[#f59e1c] text-xs font-bold flex items-center justify-center">3</span>
              Restart your AI tool
            </h3>
            <p className="text-gray-400 text-sm">
              Close and reopen Claude Desktop / Cursor / VS Code. The GitHub MCP server will load automatically.
            </p>
          </div>
        </section>

        {/* Org access fix */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Fixing Org Access</h2>
          <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-6">
            <p className="text-gray-400 text-sm mb-4">
              If you get <span className="text-red-400 font-mono">&quot;Resource not accessible by personal access token&quot;</span> on org repos:
            </p>
            <ol className="list-decimal list-inside text-sm text-gray-400 space-y-2">
              <li>When creating the PAT, select your <span className="text-white font-medium">org</span> as Resource Owner</li>
              <li>After creation, go to <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-[#f59e1c] hover:underline">github.com/settings/tokens</a></li>
              <li>Click your token &rarr; <span className="text-white font-medium">Request access</span> for your org</li>
              <li>Ask your org admin to approve at: <code className="text-gray-300 text-xs">github.com/organizations/YOUR_ORG/settings/personal-access-token-requests</code></li>
            </ol>
            <p className="text-gray-500 text-xs mt-4">
              This is a GitHub security policy, not a bug. Fine-grained PATs for org repos require explicit admin approval.
            </p>
          </div>
        </section>

        {/* Available tools */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What You Get</h2>
          <p className="text-gray-400 text-sm mb-5">
            Once configured, your AI tool can use these GitHub MCP tools:
          </p>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
            {[
              { tool: "get_file_contents", desc: "Read any file from a repo" },
              { tool: "search_code", desc: "Search code across repos" },
              { tool: "create_issue", desc: "Create a new issue" },
              { tool: "list_issues", desc: "List issues on a repo" },
              { tool: "create_pull_request", desc: "Open a PR" },
              { tool: "get_pull_request", desc: "View PR details" },
              { tool: "create_branch", desc: "Create a new branch" },
              { tool: "list_commits", desc: "View commit history" },
              { tool: "push_files", desc: "Push multiple files" },
              { tool: "create_or_update_file", desc: "Create or edit files" },
              { tool: "search_repositories", desc: "Search GitHub repos" },
              { tool: "fork_repository", desc: "Fork a repo" },
            ].map(({ tool, desc }) => (
              <div key={tool} className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-3">
                <div className="text-[#f59e1c] font-mono text-xs font-medium">{tool}</div>
                <div className="text-gray-500 text-xs mt-0.5">{desc}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Troubleshooting */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Troubleshooting</h2>
          <div className="grid gap-3">
            {[
              {
                q: "spawn npx ENOENT",
                a: os === "windows"
                  ? 'Use "cmd" with args ["/c", "npx", ...] instead of "npx" directly. Our script does this automatically.'
                  : "Make sure Node.js is in your PATH. If using NVM, the full path to npx may be needed: which npx to find it.",
              },
              {
                q: "Token expired",
                a: "Re-run the setup script to generate and configure a new token.",
              },
              {
                q: "MCP server not loading (no errors shown)",
                a: "Check your JSON config for syntax errors (no trailing commas). Try running the npx command manually in your terminal to see error output.",
              },
              {
                q: "Rate limiting (HTTP 429)",
                a: "Authenticated PATs get 5,000 requests/hour. If you hit limits, wait for the rate limit to reset (shown in response headers).",
              },
            ].map(({ q, a }) => (
              <div key={q} className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
                <div className="text-red-400 font-mono text-sm mb-2">{q}</div>
                <div className="text-gray-400 text-sm">{a}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Security */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Security</h2>
          <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-6">
            <div className="grid sm:grid-cols-2 gap-4 text-sm text-gray-400">
              <div className="flex items-start gap-2">
                <span className="text-green-400">&#10003;</span>
                <span>Token stays on your machine in local config files</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-400">&#10003;</span>
                <span>Context Bharat never receives or stores your GitHub token</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-400">&#10003;</span>
                <span>Use fine-grained tokens with minimum required permissions</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-400">&#10003;</span>
                <span>Set 90-day expiration — regenerate when needed</span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="text-center pt-8 border-t border-white/10">
          <h3 className="text-xl font-bold mb-3">Want Indian API docs too?</h3>
          <p className="text-gray-400 text-sm mb-5">
            Set up Context Bharat MCP to get Razorpay, ONDC, Zerodha, UPI docs in your AI editor.
          </p>
          <div className="flex gap-3 justify-center">
            <Link
              href="/docs"
              className="bg-[#f59e1c] text-black px-6 py-3 rounded-xl font-semibold hover:bg-[#fbbf45] transition-colors"
            >
              Set Up Context Bharat
            </Link>
            <Link
              href="/setup"
              className="border border-white/20 text-white px-6 py-3 rounded-xl font-semibold hover:bg-white/5 transition-colors"
            >
              All Setup Tools
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="font-bold text-[#f59e1c]">
            context<span className="text-white">Bharat</span>
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            <Link href="/docs" className="hover:text-white transition-colors">Install</Link>
            <Link href="/setup" className="hover:text-white transition-colors">Tools</Link>
            <Link href="/libraries" className="hover:text-white transition-colors">Libraries</Link>
            <Link href="https://github.com/contextbharat/context-bharat" className="hover:text-white transition-colors">GitHub</Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
