#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Context Bharat — MCP Server Setup Script
# Sets up Context Bharat docs MCP for Indian API documentation
# Works with: Claude Desktop, Claude Code, Cursor, VS Code
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }
step()    { echo -e "\n${CYAN}${BOLD}==> $1${NC}"; }

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     Context Bharat — Indian API Docs in Your AI Tool        ║${NC}"
echo -e "${BOLD}║  Razorpay, Zerodha, ONDC, UPI, GSTN — always up to date    ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Check Node.js ───────────────────────────────────────────────────────────
step "Step 1: Checking prerequisites"

if ! command -v node &> /dev/null; then
    error "Node.js is not installed. Install from: https://nodejs.org/ (v18+)"
    exit 1
fi
success "Node.js $(node -v) found"

# ─── API Key ─────────────────────────────────────────────────────────────────
step "Step 2: Context Bharat API Key"

echo ""
echo "  Context Bharat is free to use (200 queries/day, no card required)."
echo ""
echo "  Get your free API key:"
echo "    1. Go to: https://contextbharat.com/dashboard"
echo "    2. Sign up with Google or email"
echo "    3. Copy your API key from the dashboard"
echo ""
echo "  Or skip to use without a key (100 queries/day, top 30 libraries)."
echo ""

read -rp "Paste your API key (or press Enter to skip): " CB_API_KEY

if [ -z "$CB_API_KEY" ]; then
    info "No key provided. Setting up in free mode (100 queries/day)."
    MCP_ARGS='["-y", "@contextbharat/mcp"]'
else
    MCP_ARGS="[\"-y\", \"@contextbharat/mcp\", \"--api-key\", \"$CB_API_KEY\"]"
fi

# ─── Detect tools ────────────────────────────────────────────────────────────
step "Step 3: Configuring AI tools"

if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
else
    PLATFORM="linux"
fi

# Claude Desktop
CLAUDE_DESKTOP_CONFIG=""
if [[ "$PLATFORM" == "macos" ]]; then
    CLAUDE_DESKTOP_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
else
    CLAUDE_DESKTOP_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
fi

CLAUDE_CODE_CONFIG="$HOME/.claude.json"

configure_tool() {
    local config_path="$1"
    local tool_name="$2"

    mkdir -p "$(dirname "$config_path")"

    if [ -f "$config_path" ]; then
        cp "$config_path" "${config_path}.backup.$(date +%Y%m%d%H%M%S)"
    fi

    local mcp_config
    if [ -z "$CB_API_KEY" ]; then
        mcp_config='{"command":"npx","args":["-y","@contextbharat/mcp"]}'
    else
        mcp_config="{\"command\":\"npx\",\"args\":[\"-y\",\"@contextbharat/mcp\",\"--api-key\",\"$CB_API_KEY\"]}"
    fi

    node -e "
const fs = require('fs');
let config = {};
try { config = JSON.parse(fs.readFileSync('$config_path', 'utf8')); } catch {}
if (!config.mcpServers) config.mcpServers = {};
config.mcpServers.contextbharat = $mcp_config;
fs.writeFileSync('$config_path', JSON.stringify(config, null, 2));
"
    success "$tool_name configured at: $config_path"
}

# Configure Claude Desktop
if [ -d "$(dirname "$CLAUDE_DESKTOP_CONFIG")" ]; then
    read -rp "Configure for Claude Desktop? [Y/n] " confirm
    if [[ ! "$confirm" =~ ^[Nn] ]]; then
        configure_tool "$CLAUDE_DESKTOP_CONFIG" "Claude Desktop"
    fi
fi

# Configure Claude Code
if command -v claude &> /dev/null || [ -f "$CLAUDE_CODE_CONFIG" ]; then
    read -rp "Configure for Claude Code? [Y/n] " confirm
    if [[ ! "$confirm" =~ ^[Nn] ]]; then
        configure_tool "$CLAUDE_CODE_CONFIG" "Claude Code"
    fi
fi

# Manual config for others
echo ""
echo -e "${BOLD}For Cursor / VS Code / Windsurf — add this to MCP settings:${NC}"
echo ""
if [ -z "$CB_API_KEY" ]; then
    cat <<'EOF'
{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp"]
    }
  }
}
EOF
else
    cat <<EOF
{
  "mcpServers": {
    "contextbharat": {
      "command": "npx",
      "args": ["-y", "@contextbharat/mcp", "--api-key", "$CB_API_KEY"]
    }
  }
}
EOF
fi

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}Setup Complete!${NC}"
echo ""
echo -e "  ${BOLD}Try these in your AI tool:${NC}"
echo "    'How do I create a Razorpay payment link? use contextbharat'"
echo "    'Show me ONDC Beckn Protocol buyer flow use contextbharat'"
echo "    'Zerodha Kite API place order example use contextbharat'"
echo ""
echo -e "  ${BOLD}Also set up GitHub MCP:${NC}"
echo "    bash tools/setup-github-mcp.sh"
echo ""
