# GitHub MCP Setup Guide

Use GitHub directly from Claude, Cursor, or VS Code — create issues, read code, open PRs without leaving your AI tool.

---

## The Problem

The official GitHub MCP server uses OAuth which requires **org-level admin approval**. If your org admin hasn't approved it, you get "account doesn't have org level access" — even though your personal repos work fine.

**The fix:** Use a Personal Access Token (PAT) instead. Our setup script automates this in 2 minutes.

---

## Quick Setup (Recommended)

```bash
# One command — guides you through everything
make setup-github-mcp

# Or directly:
bash tools/setup-github-mcp.sh
```

The script will:
1. Check Node.js is installed (v18+ required)
2. Guide you through creating a GitHub PAT
3. Verify the token works
4. Auto-detect your AI tools (Claude Desktop, Claude Code, Cursor, VS Code)
5. Configure the GitHub MCP server in the right config file
6. Optionally save the token to your shell profile

---

## Manual Setup

If you prefer to do it manually:

### Step 1: Create a Fine-Grained PAT

1. Go to: https://github.com/settings/tokens?type=beta
2. Click **Generate new token**
3. Settings:
   - **Token name:** `MCP Server`
   - **Expiration:** 90 days
   - **Resource owner:** Your account or org
4. **Repository access:** All repositories (or select specific ones)
5. **Permissions** (under Repository permissions):
   - Contents: **Read-only**
   - Issues: **Read and write**
   - Pull requests: **Read and write**
   - Metadata: **Read-only** (auto-selected)
6. Click **Generate token** and copy it

### Step 2: Add to Your AI Tool

**Claude Desktop** (`~/.config/Claude/claude_desktop_config.json` on Linux, `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

**Claude Code** (`~/.claude.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

**Cursor:** Settings > MCP Servers > Add New
- Name: `github`
- Command: `npx -y @modelcontextprotocol/server-github`
- Environment: `GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_YOUR_TOKEN_HERE`

### Step 3: Restart Your AI Tool

Close and reopen Claude Desktop/Cursor/VS Code for the MCP server to load.

---

## For Org Repos

If you need access to organization repositories:

1. When creating the PAT, select the **org** as Resource Owner
2. Your org admin needs to approve the token
3. Go to https://github.com/settings/tokens → click your token → **Request access** for the org
4. Ask your org admin to approve at: `https://github.com/organizations/YOUR_ORG/settings/personal-access-token-requests`

**Why this happens:** Fine-grained PATs for org repos require explicit org approval as a security measure. This is a GitHub policy, not a bug.

---

## Available GitHub MCP Tools

Once configured, your AI tool can:

| Tool | What it does |
|------|-------------|
| `search_repositories` | Search GitHub for repos |
| `get_file_contents` | Read any file from a repo |
| `create_or_update_file` | Create or edit files |
| `push_files` | Push multiple files at once |
| `create_issue` | Create a new issue |
| `list_issues` | List issues on a repo |
| `create_pull_request` | Open a PR |
| `get_pull_request` | View PR details |
| `create_branch` | Create a new branch |
| `list_commits` | View commit history |
| `search_code` | Search code across repos |
| `fork_repository` | Fork a repo |

---

## Troubleshooting

**"Token expired"**
Re-run `make setup-github-mcp` with a new token.

**"Resource not accessible by personal access token"**
Your token doesn't have the required permissions. Regenerate with the permissions listed in Step 1.

**"Not Found" on org repos**
Your org hasn't approved the token. See "For Org Repos" section above.

**MCP server not loading**
1. Check Node.js v18+ is installed: `node -v`
2. Check npx works: `npx --version`
3. Try running manually: `GITHUB_PERSONAL_ACCESS_TOKEN=your_token npx -y @modelcontextprotocol/server-github`
4. Check your config file for JSON syntax errors

**Rate limiting**
Authenticated requests get 5,000 requests/hour (vs 60 without auth). If you hit limits, the MCP server will return errors until the limit resets.

---

## Security Notes

- Your PAT **stays on your machine** — it's stored in your local MCP config file only
- Context Bharat **never** receives or stores your GitHub token
- Use **fine-grained tokens** (not classic tokens) for minimum required permissions
- Set a **90-day expiration** and regenerate when needed
- Never commit your PAT to version control

---

## Set Up Everything at Once

Want GitHub MCP + Indian API docs in one go?

```bash
make setup-all-mcp
```

This sets up both:
- **GitHub MCP** — repos, issues, PRs
- **Context Bharat MCP** — Razorpay, ONDC, Zerodha, UPI documentation
