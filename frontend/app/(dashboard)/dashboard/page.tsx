/**
 * User dashboard — API keys + usage analytics + MCP setup guide + query sandbox.
 */
import { ApiKeyManager } from "@/components/api-key-manager";
import { QueryTester } from "@/components/query-tester";
import { UsageChart } from "@/components/usage-chart";
import { FeatureCards } from "@/components/feature-cards";

export const metadata = {
  title: "Dashboard — contextBharat",
  description: "Manage your API keys and test documentation queries.",
};

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[#05080f]">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-10">
          <div className="font-bold text-[#f59e1c] text-xl mb-1">
            context<span className="text-white">Bharat</span>
          </div>
          <h1 className="text-white text-2xl font-semibold mt-4">Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">
            Manage your API keys, monitor usage, and test documentation queries
          </p>
        </div>

        <div className="grid gap-8">
          {/* Usage Analytics */}
          <section>
            <h2 className="text-white font-semibold mb-4">Usage Analytics</h2>
            <UsageChart />
          </section>

          {/* API Keys */}
          <section>
            <h2 className="text-white font-semibold mb-4">API Keys</h2>
            <ApiKeyManager />
          </section>

          {/* MCP Setup */}
          <section>
            <h2 className="text-white font-semibold mb-4">Quick Setup</h2>
            <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
              <p className="text-gray-400 text-sm mb-4">
                Add to your Claude Desktop or Cursor config:
              </p>
              <pre className="bg-black/40 rounded-lg p-4 text-sm text-green-300 font-mono overflow-x-auto">
{`{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp", "--api-key", "YOUR_API_KEY"]
    }
  }
}`}
              </pre>
              <p className="text-gray-500 text-xs mt-3">
                Then type <code className="text-[#f59e1c]">use contextbharat</code> in any Claude
                or Cursor prompt.
              </p>

              {/* Remote MCP (Pro) */}
              <div className="mt-4 pt-4 border-t border-[#1e2d44]">
                <p className="text-gray-400 text-sm mb-2">
                  Or use the remote MCP server (Pro tier):
                </p>
                <pre className="bg-black/40 rounded-lg p-4 text-sm text-green-300 font-mono overflow-x-auto">
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
            </div>
          </section>

          {/* MCP Connection Status */}
          <section>
            <h2 className="text-white font-semibold mb-4">Connection Status</h2>
            <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <span className="w-2 h-2 bg-green-400 rounded-full" />
                    <span className="text-sm text-white font-medium">API</span>
                  </div>
                  <div className="text-xs text-gray-500">api.contextbharat.com</div>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <span className="w-2 h-2 bg-green-400 rounded-full" />
                    <span className="text-sm text-white font-medium">MCP Server</span>
                  </div>
                  <div className="text-xs text-gray-500">mcp.contextbharat.com</div>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <span className="w-2 h-2 bg-green-400 rounded-full" />
                    <span className="text-sm text-white font-medium">Index</span>
                  </div>
                  <div className="text-xs text-gray-500">Last refresh: 2 AM IST</div>
                </div>
              </div>
            </div>
          </section>

          {/* Features */}
          <FeatureCards />

          {/* Query Sandbox */}
          <section>
            <h2 className="text-white font-semibold mb-4">Try It Now</h2>
            <QueryTester defaultLibraryId="/razorpay/razorpay-sdk" />
          </section>
        </div>
      </div>
    </div>
  );
}
