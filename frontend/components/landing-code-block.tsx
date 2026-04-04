/**
 * LandingCodeBlock — the MCP config install snippet with copy button.
 * Used on the landing page hero section.
 */
"use client";

import { CodeBlock } from "@/components/code-block";

const MCP_CONFIG = `{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp"]
    }
  }
}`;

export function LandingCodeBlock() {
  return (
    <div className="relative">
      <div className="flex items-center justify-between mb-3 px-1">
        <span className="text-gray-500 text-xs">Add to Claude / Cursor / VS Code</span>
        <span className="text-green-400 text-xs flex items-center gap-1">
          <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
          MCP Compatible
        </span>
      </div>
      <CodeBlock code={MCP_CONFIG} language="json" showHeader={true} />
      <p className="text-gray-500 text-xs mt-3 px-1">
        Then type <code className="text-[#f59e1c] font-semibold">use contextbharat</code> in
        any prompt. That&apos;s it.
      </p>
    </div>
  );
}
