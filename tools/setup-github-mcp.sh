#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Context Bharat — GitHub MCP Setup Script
# Sets up the official GitHub MCP server locally using your Personal Access Token
# Works with: Claude Desktop, Claude Code, Cursor, VS Code (Copilot)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ─── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ─── Helpers ─────────────────────────────────────────────────────────────────
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }
step()    { echo -e "\n${CYAN}${BOLD}==> $1${NC}"; }

# ─── Banner ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║        Context Bharat — GitHub MCP Setup                    ║${NC}"
echo -e "${BOLD}║  Use GitHub repos, issues, PRs directly in your AI tool     ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Step 1: Check prerequisites ────────────────────────────────────────────
step "Step 1: Checking prerequisites"

# Check Node.js
if ! command -v node &> /dev/null; then
    error "Node.js is not installed."
    echo "  Install it from: https://nodejs.org/ (v18+ required)"
    echo "  Or use nvm:  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
    exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    error "Node.js v18+ required. You have $(node -v)"
    exit 1
fi
success "Node.js $(node -v) found"

# Check npx
if ! command -v npx &> /dev/null; then
    error "npx not found. Install Node.js v18+ which includes npx."
    exit 1
fi
success "npx available"

# ─── Step 2: Guide PAT creation ─────────────────────────────────────────────
step "Step 2: GitHub Personal Access Token (PAT)"

echo ""
echo -e "The GitHub MCP server needs a Personal Access Token to access your repos."
echo -e "This token ${BOLD}stays on your machine${NC} — it is never sent to Context Bharat."
echo ""

# Check if PAT already exists in environment
EXISTING_PAT=""
if [ -n "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]; then
    EXISTING_PAT="$GITHUB_PERSONAL_ACCESS_TOKEN"
    success "Found existing GITHUB_PERSONAL_ACCESS_TOKEN in environment"
elif [ -n "${GITHUB_TOKEN:-}" ]; then
    EXISTING_PAT="$GITHUB_TOKEN"
    success "Found existing GITHUB_TOKEN in environment"
fi

if [ -n "$EXISTING_PAT" ]; then
    echo -e "  Token prefix: ${CYAN}${EXISTING_PAT:0:8}...${NC}"
    echo ""
    read -rp "Use this existing token? [Y/n] " use_existing
    if [[ "$use_existing" =~ ^[Nn] ]]; then
        EXISTING_PAT=""
    fi
fi

if [ -z "$EXISTING_PAT" ]; then
    echo -e "${BOLD}How to create a GitHub PAT (takes 2 minutes):${NC}"
    echo ""
    echo "  1. Open: https://github.com/settings/tokens?type=beta"
    echo "     (Fine-grained tokens — more secure than classic tokens)"
    echo ""
    echo "  2. Click 'Generate new token'"
    echo ""
    echo "  3. Settings:"
    echo "     - Token name:    'MCP Server' (or anything you like)"
    echo "     - Expiration:    90 days (you can regenerate later)"
    echo "     - Resource owner: Select your account (or your org)"
    echo ""
    echo "  4. Repository access:"
    echo "     - 'All repositories' for full access, OR"
    echo "     - 'Only select repositories' for specific repos"
    echo ""
    echo "  5. Permissions (expand 'Repository permissions'):"
    echo "     - Contents:       Read-only   (read code and files)"
    echo "     - Issues:         Read & Write (view and create issues)"
    echo "     - Pull requests:  Read & Write (view and create PRs)"
    echo "     - Metadata:       Read-only   (auto-selected)"
    echo ""
    echo "  6. Click 'Generate token' and copy it"
    echo ""
    echo -e "  ${YELLOW}For org repos: Your org admin may need to approve the token.${NC}"
    echo -e "  ${YELLOW}Go to: https://github.com/settings/tokens → token → Request org access${NC}"
    echo ""

    # Attempt to open browser
    if command -v xdg-open &> /dev/null; then
        read -rp "Open GitHub token page in your browser? [Y/n] " open_browser
        if [[ ! "$open_browser" =~ ^[Nn] ]]; then
            xdg-open "https://github.com/settings/tokens?type=beta" 2>/dev/null || true
        fi
    elif command -v open &> /dev/null; then
        read -rp "Open GitHub token page in your browser? [Y/n] " open_browser
        if [[ ! "$open_browser" =~ ^[Nn] ]]; then
            open "https://github.com/settings/tokens?type=beta" 2>/dev/null || true
        fi
    fi

    echo ""
    read -rsp "Paste your GitHub PAT here (input is hidden): " GITHUB_PAT
    echo ""

    if [ -z "$GITHUB_PAT" ]; then
        error "No token provided. Exiting."
        exit 1
    fi

    # Basic validation
    if [[ ! "$GITHUB_PAT" =~ ^(ghp_|github_pat_) ]]; then
        warn "Token doesn't start with 'ghp_' or 'github_pat_'. Make sure you copied the full token."
        read -rp "Continue anyway? [y/N] " continue_anyway
        if [[ ! "$continue_anyway" =~ ^[Yy] ]]; then
            exit 1
        fi
    fi
else
    GITHUB_PAT="$EXISTING_PAT"
fi

# ─── Step 3: Verify token works ─────────────────────────────────────────────
step "Step 3: Verifying token"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $GITHUB_PAT" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/user" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    # Get username for display
    GH_USER=$(curl -s \
        -H "Authorization: Bearer $GITHUB_PAT" \
        -H "Accept: application/vnd.github+json" \
        "https://api.github.com/user" 2>/dev/null | grep -o '"login":"[^"]*"' | head -1 | cut -d'"' -f4)
    success "Token valid! Authenticated as: ${CYAN}$GH_USER${NC}"
elif [ "$HTTP_CODE" = "401" ]; then
    error "Token is invalid or expired. Please check and try again."
    exit 1
elif [ "$HTTP_CODE" = "403" ]; then
    warn "Token works but has limited permissions. GitHub MCP may have restricted functionality."
    echo "  Consider regenerating with the permissions listed in Step 2."
else
    warn "Could not verify token (HTTP $HTTP_CODE). Continuing anyway..."
    echo "  This might be a network issue. The token may still work."
fi

# ─── Step 4: Detect AI tools ────────────────────────────────────────────────
step "Step 4: Detecting installed AI tools"

TOOLS_FOUND=()

# Claude Desktop (macOS)
CLAUDE_DESKTOP_CONFIG_MAC="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
# Claude Desktop (Linux)
CLAUDE_DESKTOP_CONFIG_LINUX="$HOME/.config/Claude/claude_desktop_config.json"
# Claude Code
CLAUDE_CODE_CONFIG="$HOME/.claude.json"
# Cursor
CURSOR_CONFIG_MAC="$HOME/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
CURSOR_CONFIG_LINUX="$HOME/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
# VS Code
VSCODE_CONFIG_MAC="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
VSCODE_CONFIG_LINUX="$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
else
    PLATFORM="linux"
fi

# Check Claude Desktop
if [[ "$PLATFORM" == "macos" ]] && [ -d "$(dirname "$CLAUDE_DESKTOP_CONFIG_MAC")" ]; then
    TOOLS_FOUND+=("claude-desktop")
    info "Found: Claude Desktop"
elif [[ "$PLATFORM" == "linux" ]] && [ -d "$(dirname "$CLAUDE_DESKTOP_CONFIG_LINUX")" ]; then
    TOOLS_FOUND+=("claude-desktop")
    info "Found: Claude Desktop"
fi

# Check Claude Code
if command -v claude &> /dev/null || [ -f "$CLAUDE_CODE_CONFIG" ]; then
    TOOLS_FOUND+=("claude-code")
    info "Found: Claude Code (CLI)"
fi

# Check Cursor
if command -v cursor &> /dev/null; then
    TOOLS_FOUND+=("cursor")
    info "Found: Cursor"
fi

# Check VS Code
if command -v code &> /dev/null; then
    TOOLS_FOUND+=("vscode")
    info "Found: VS Code"
fi

if [ ${#TOOLS_FOUND[@]} -eq 0 ]; then
    warn "No AI tools auto-detected. We'll generate config you can paste manually."
    TOOLS_FOUND+=("manual")
fi

# ─── Step 5: Configure MCP servers ──────────────────────────────────────────
step "Step 5: Configuring GitHub MCP server"

# The GitHub MCP server npm package
GITHUB_MCP_PKG="@modelcontextprotocol/server-github"

# Build the MCP server config JSON block
MCP_CONFIG=$(cat <<EOF
{
  "command": "npx",
  "args": ["-y", "$GITHUB_MCP_PKG"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_PAT"
  }
}
EOF
)

configure_claude_desktop() {
    local config_path
    if [[ "$PLATFORM" == "macos" ]]; then
        config_path="$CLAUDE_DESKTOP_CONFIG_MAC"
    else
        config_path="$CLAUDE_DESKTOP_CONFIG_LINUX"
    fi

    mkdir -p "$(dirname "$config_path")"

    if [ -f "$config_path" ]; then
        # Backup existing config
        cp "$config_path" "${config_path}.backup.$(date +%Y%m%d%H%M%S)"
        success "Backed up existing config"

        # Check if github server already configured
        if grep -q '"github"' "$config_path" 2>/dev/null; then
            warn "GitHub MCP already configured in Claude Desktop. Updating..."
        fi

        # Use node to safely merge JSON
        node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$config_path', 'utf8'));
if (!config.mcpServers) config.mcpServers = {};
config.mcpServers.github = $MCP_CONFIG;
fs.writeFileSync('$config_path', JSON.stringify(config, null, 2));
console.log('Config updated successfully');
"
    else
        # Create new config
        node -e "
const fs = require('fs');
const config = { mcpServers: { github: $MCP_CONFIG } };
fs.writeFileSync('$config_path', JSON.stringify(config, null, 2));
console.log('Config created successfully');
"
    fi

    success "Claude Desktop configured at: $config_path"
    warn "Restart Claude Desktop for changes to take effect"
}

configure_claude_code() {
    local config_path="$CLAUDE_CODE_CONFIG"

    if [ -f "$config_path" ]; then
        cp "$config_path" "${config_path}.backup.$(date +%Y%m%d%H%M%S)"
        success "Backed up existing config"

        node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$config_path', 'utf8'));
if (!config.mcpServers) config.mcpServers = {};
config.mcpServers.github = $MCP_CONFIG;
fs.writeFileSync('$config_path', JSON.stringify(config, null, 2));
console.log('Config updated successfully');
"
    else
        node -e "
const fs = require('fs');
const config = { mcpServers: { github: $MCP_CONFIG } };
fs.writeFileSync('$config_path', JSON.stringify(config, null, 2));
console.log('Config created successfully');
"
    fi

    success "Claude Code configured at: $config_path"
}

print_manual_config() {
    echo ""
    echo -e "${BOLD}Add this to your MCP config file:${NC}"
    echo ""
    echo -e "${CYAN}For Claude Desktop${NC} (~/.config/Claude/claude_desktop_config.json or ~/Library/Application Support/Claude/claude_desktop_config.json):"
    echo ""
    cat <<EOF
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "$GITHUB_MCP_PKG"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_PAT"
      }
    }
  }
}
EOF
    echo ""
    echo -e "${CYAN}For Claude Code${NC} (~/.claude.json):"
    echo ""
    cat <<EOF
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "$GITHUB_MCP_PKG"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_PAT"
      }
    }
  }
}
EOF
    echo ""
    echo -e "${CYAN}For Cursor${NC} (Settings > MCP Servers > Add):"
    echo "  Name:    github"
    echo "  Command: npx -y $GITHUB_MCP_PKG"
    echo "  Env:     GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PAT"
    echo ""
}

# Configure each detected tool
for tool in "${TOOLS_FOUND[@]}"; do
    case "$tool" in
        "claude-desktop")
            echo ""
            read -rp "Configure GitHub MCP for Claude Desktop? [Y/n] " confirm
            if [[ ! "$confirm" =~ ^[Nn] ]]; then
                configure_claude_desktop
            fi
            ;;
        "claude-code")
            echo ""
            read -rp "Configure GitHub MCP for Claude Code? [Y/n] " confirm
            if [[ ! "$confirm" =~ ^[Nn] ]]; then
                configure_claude_code
            fi
            ;;
        "cursor"|"vscode")
            echo ""
            echo -e "${YELLOW}$tool detected but requires manual MCP config.${NC}"
            print_manual_config
            ;;
        "manual")
            print_manual_config
            ;;
    esac
done

# ─── Step 6: Save token to shell profile (optional) ─────────────────────────
step "Step 6: Save token to shell profile (optional)"

echo ""
echo "Optionally save the token as an environment variable so other tools can use it."
echo "This adds GITHUB_PERSONAL_ACCESS_TOKEN to your shell profile."
echo ""
read -rp "Save to shell profile? [y/N] " save_profile

if [[ "$save_profile" =~ ^[Yy] ]]; then
    # Detect shell profile
    SHELL_PROFILE=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_PROFILE="$HOME/.bash_profile"
    fi

    if [ -n "$SHELL_PROFILE" ]; then
        # Check if already exists
        if grep -q "GITHUB_PERSONAL_ACCESS_TOKEN" "$SHELL_PROFILE" 2>/dev/null; then
            warn "GITHUB_PERSONAL_ACCESS_TOKEN already in $SHELL_PROFILE. Skipping."
        else
            echo "" >> "$SHELL_PROFILE"
            echo "# GitHub PAT for MCP Server (added by Context Bharat setup)" >> "$SHELL_PROFILE"
            echo "export GITHUB_PERSONAL_ACCESS_TOKEN=\"$GITHUB_PAT\"" >> "$SHELL_PROFILE"
            success "Saved to $SHELL_PROFILE"
            info "Run 'source $SHELL_PROFILE' or open a new terminal to activate"
        fi
    else
        warn "Could not detect shell profile. Add this manually:"
        echo "  export GITHUB_PERSONAL_ACCESS_TOKEN=\"$GITHUB_PAT\""
    fi
else
    info "Skipped. Token is configured in MCP config only."
fi

# ─── Step 7: Test ────────────────────────────────────────────────────────────
step "Step 7: Quick test"

echo ""
echo "Testing GitHub MCP server starts correctly..."
echo ""

# Test that the package can be fetched
if npx -y "$GITHUB_MCP_PKG" --help &>/dev/null; then
    success "GitHub MCP server package loads correctly"
else
    # Some MCP servers don't have --help, try a different approach
    info "Package downloaded. MCP server will start when your AI tool connects."
fi

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║                   Setup Complete!                            ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}What you can now do in Claude/Cursor:${NC}"
echo ""
echo "    'Create an issue on my-org/my-repo for the login bug'"
echo "    'List open PRs on my-org/my-repo'"
echo "    'Read the README from my-org/my-repo'"
echo "    'Search for authentication code in my-org/my-repo'"
echo ""
echo -e "  ${BOLD}Available GitHub MCP tools:${NC}"
echo "    - create_or_update_file   - push_files"
echo "    - search_repositories     - create_repository"
echo "    - get_file_contents       - create_issue"
echo "    - create_pull_request     - fork_repository"
echo "    - create_branch           - list_commits"
echo "    - list_issues             - search_code"
echo "    - search_issues           - get_pull_request"
echo ""
echo -e "  ${YELLOW}Remember:${NC} Restart your AI tool after setup for changes to take effect."
echo ""
echo -e "  ${CYAN}Also try Context Bharat for Indian API docs:${NC}"
echo "    bash tools/setup-contextbharat-mcp.sh"
echo "    (Razorpay, Zerodha, ONDC, UPI docs in your AI tool)"
echo ""
echo -e "  ${BOLD}Troubleshooting:${NC}"
echo "    - Token expired?      Re-run this script with a new token"
echo "    - Org access denied?  Ask org admin at: https://github.com/settings/tokens"
echo "    - MCP not loading?    Check: https://contextbharat.com/docs/github-mcp-troubleshoot"
echo ""
echo -e "  Questions? https://github.com/contextbharat/context-bharat/issues"
echo ""
