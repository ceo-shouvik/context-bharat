#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Context Bharat — Complete MCP Setup
# One script to set up both Context Bharat + GitHub MCP servers
# Run: curl -fsSL https://contextbharat.com/setup.sh | bash
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║          Context Bharat — Complete MCP Setup                 ║${NC}"
echo -e "${BOLD}║  Indian API docs + GitHub access in your AI coding tool      ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "This will set up:"
echo "  1. Context Bharat MCP  — Razorpay, Zerodha, ONDC, UPI docs"
echo "  2. GitHub MCP          — Repos, issues, PRs (with your PAT)"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Context Bharat MCP ─────────────────────────────────────────────────────
echo -e "${CYAN}${BOLD}━━━ Part 1: Context Bharat MCP ━━━${NC}"
bash "$SCRIPT_DIR/setup-contextbharat-mcp.sh"

echo ""
echo -e "${CYAN}${BOLD}━━━ Part 2: GitHub MCP ━━━${NC}"
echo ""
read -rp "Also set up GitHub MCP server? [Y/n] " setup_github
if [[ ! "$setup_github" =~ ^[Nn] ]]; then
    bash "$SCRIPT_DIR/setup-github-mcp.sh"
fi

echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║              All MCP Servers Configured!                     ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${YELLOW}Restart your AI tool (Claude/Cursor/VS Code) to activate.${NC}"
echo ""
echo "  Your AI tool now has:"
echo "    - Indian API documentation (Razorpay, ONDC, UPI, Zerodha...)"
echo "    - GitHub access (repos, issues, PRs, code search)"
echo ""
echo "  Try: 'Create a Razorpay payment integration and open a PR for it'"
echo ""
