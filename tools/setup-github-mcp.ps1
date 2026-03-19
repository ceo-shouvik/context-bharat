# ─────────────────────────────────────────────────────────────────────────────
# Context Bharat — GitHub MCP Setup Script (Windows PowerShell)
# Sets up the official GitHub MCP server locally using your Personal Access Token
# Works with: Claude Desktop, Claude Code, Cursor, VS Code
# Run: powershell -ExecutionPolicy Bypass -File setup-github-mcp.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor White
Write-Host "║        Context Bharat — GitHub MCP Setup (Windows)          ║" -ForegroundColor White
Write-Host "║  Use GitHub repos, issues, PRs directly in your AI tool     ║" -ForegroundColor White
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor White
Write-Host ""

# ─── Step 1: Check prerequisites ────────────────────────────────────────────
Write-Step "Step 1: Checking prerequisites"

try {
    $nodeVersion = (node -v) -replace 'v', ''
    $nodeMajor = [int]($nodeVersion.Split('.')[0])
    if ($nodeMajor -lt 18) {
        Write-Err "Node.js v18+ required. You have v$nodeVersion"
        Write-Host "  Download from: https://nodejs.org/"
        exit 1
    }
    Write-Ok "Node.js v$nodeVersion found"
} catch {
    Write-Err "Node.js is not installed."
    Write-Host "  Download from: https://nodejs.org/ (v18+ required)"
    Write-Host "  Or use: winget install OpenJS.NodeJS.LTS"
    exit 1
}

try {
    npx --version | Out-Null
    Write-Ok "npx available"
} catch {
    Write-Err "npx not found. Reinstall Node.js v18+."
    exit 1
}

# ─── Step 2: Guide PAT creation ─────────────────────────────────────────────
Write-Step "Step 2: GitHub Personal Access Token (PAT)"

Write-Host ""
Write-Host "The GitHub MCP server needs a Personal Access Token to access your repos."
Write-Host "This token STAYS ON YOUR MACHINE — it is never sent to Context Bharat."
Write-Host ""

# Check environment
$existingPat = $null
if ($env:GITHUB_PERSONAL_ACCESS_TOKEN) {
    $existingPat = $env:GITHUB_PERSONAL_ACCESS_TOKEN
    Write-Ok "Found existing GITHUB_PERSONAL_ACCESS_TOKEN in environment"
} elseif ($env:GITHUB_TOKEN) {
    $existingPat = $env:GITHUB_TOKEN
    Write-Ok "Found existing GITHUB_TOKEN in environment"
}

if ($existingPat) {
    $prefix = $existingPat.Substring(0, [Math]::Min(8, $existingPat.Length))
    Write-Host "  Token prefix: $prefix..."
    $useExisting = Read-Host "Use this existing token? [Y/n]"
    if ($useExisting -eq 'n' -or $useExisting -eq 'N') {
        $existingPat = $null
    }
}

if (-not $existingPat) {
    Write-Host ""
    Write-Host "How to create a GitHub PAT (takes 2 minutes):" -ForegroundColor White
    Write-Host ""
    Write-Host "  1. Open: https://github.com/settings/tokens?type=beta"
    Write-Host "     (Fine-grained tokens — more secure than classic tokens)"
    Write-Host ""
    Write-Host "  2. Click 'Generate new token'"
    Write-Host ""
    Write-Host "  3. Settings:"
    Write-Host "     - Token name:    'MCP Server'"
    Write-Host "     - Expiration:    90 days"
    Write-Host "     - Resource owner: Your account (or your org)"
    Write-Host ""
    Write-Host "  4. Repository access:"
    Write-Host "     - 'All repositories' for full access, OR"
    Write-Host "     - 'Only select repositories' for specific repos"
    Write-Host ""
    Write-Host "  5. Permissions (expand 'Repository permissions'):"
    Write-Host "     - Contents:       Read-only   (read code and files)"
    Write-Host "     - Issues:         Read & Write (view and create issues)"
    Write-Host "     - Pull requests:  Read & Write (view and create PRs)"
    Write-Host "     - Metadata:       Read-only   (auto-selected)"
    Write-Host ""
    Write-Host "  6. Click 'Generate token' and copy it"
    Write-Host ""
    Write-Host "  For org repos: Your org admin may need to approve the token." -ForegroundColor Yellow
    Write-Host ""

    $openBrowser = Read-Host "Open GitHub token page in your browser? [Y/n]"
    if ($openBrowser -ne 'n' -and $openBrowser -ne 'N') {
        Start-Process "https://github.com/settings/tokens?type=beta"
    }

    Write-Host ""
    $githubPat = Read-Host "Paste your GitHub PAT here" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($githubPat)
    $githubPatPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($BSTR)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)

    if (-not $githubPatPlain) {
        Write-Err "No token provided. Exiting."
        exit 1
    }

    if (-not ($githubPatPlain -match '^(ghp_|github_pat_)')) {
        Write-Warn "Token doesn't start with 'ghp_' or 'github_pat_'. Make sure you copied the full token."
        $cont = Read-Host "Continue anyway? [y/N]"
        if ($cont -ne 'y' -and $cont -ne 'Y') { exit 1 }
    }
} else {
    $githubPatPlain = $existingPat
}

# ─── Step 3: Verify token ───────────────────────────────────────────────────
Write-Step "Step 3: Verifying token"

try {
    $headers = @{ "Authorization" = "Bearer $githubPatPlain"; "Accept" = "application/vnd.github+json" }
    $response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -ErrorAction Stop
    Write-Ok "Token valid! Authenticated as: $($response.login)"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 401) {
        Write-Err "Token is invalid or expired. Please check and try again."
        exit 1
    } elseif ($statusCode -eq 403) {
        Write-Warn "Token works but has limited permissions."
    } else {
        Write-Warn "Could not verify token (HTTP $statusCode). Continuing anyway..."
    }
}

# ─── Step 4: Detect AI tools ────────────────────────────────────────────────
Write-Step "Step 4: Detecting installed AI tools"

$toolsFound = @()

# Claude Desktop (Windows)
$claudeDesktopConfig = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
if (Test-Path (Split-Path $claudeDesktopConfig)) {
    $toolsFound += "claude-desktop"
    Write-Host "[INFO] Found: Claude Desktop" -ForegroundColor Blue
}

# Claude Code
$claudeCodeConfig = Join-Path $env:USERPROFILE ".claude.json"
if ((Get-Command claude -ErrorAction SilentlyContinue) -or (Test-Path $claudeCodeConfig)) {
    $toolsFound += "claude-code"
    Write-Host "[INFO] Found: Claude Code (CLI)" -ForegroundColor Blue
}

# Cursor
if (Get-Command cursor -ErrorAction SilentlyContinue) {
    $toolsFound += "cursor"
    Write-Host "[INFO] Found: Cursor" -ForegroundColor Blue
}

# VS Code
if (Get-Command code -ErrorAction SilentlyContinue) {
    $toolsFound += "vscode"
    Write-Host "[INFO] Found: VS Code" -ForegroundColor Blue
}

if ($toolsFound.Count -eq 0) {
    $toolsFound += "manual"
    Write-Warn "No AI tools auto-detected. We'll generate config you can paste manually."
}

# ─── Step 5: Configure ──────────────────────────────────────────────────────
Write-Step "Step 5: Configuring GitHub MCP server"

$mcpServerPkg = "@modelcontextprotocol/server-github"

# IMPORTANT: Windows needs cmd wrapper for npx
$mcpConfig = @{
    command = "cmd"
    args = @("/c", "npx", "-y", $mcpServerPkg)
    env = @{
        GITHUB_PERSONAL_ACCESS_TOKEN = $githubPatPlain
    }
}

function Configure-McpTool {
    param([string]$configPath, [string]$toolName)

    $dir = Split-Path $configPath
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

    if (Test-Path $configPath) {
        $backupPath = "$configPath.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
        Copy-Item $configPath $backupPath
        Write-Ok "Backed up existing config to $backupPath"
        $config = Get-Content $configPath -Raw | ConvertFrom-Json -AsHashtable
    } else {
        $config = @{}
    }

    if (-not $config.ContainsKey("mcpServers")) { $config["mcpServers"] = @{} }
    $config["mcpServers"]["github"] = $mcpConfig

    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Ok "$toolName configured at: $configPath"
}

function Print-ManualConfig {
    Write-Host ""
    Write-Host "Add this to your MCP config file:" -ForegroundColor White
    Write-Host ""
    $manualJson = @{
        mcpServers = @{
            github = @{
                command = "cmd"
                args = @("/c", "npx", "-y", $mcpServerPkg)
                env = @{
                    GITHUB_PERSONAL_ACCESS_TOKEN = $githubPatPlain
                }
            }
        }
    } | ConvertTo-Json -Depth 10
    Write-Host $manualJson -ForegroundColor Green
    Write-Host ""
    Write-Host "NOTE: On Windows, use 'cmd' + '/c' + 'npx' instead of just 'npx'" -ForegroundColor Yellow
    Write-Host "      This prevents the common 'spawn npx ENOENT' error." -ForegroundColor Yellow
    Write-Host ""
}

foreach ($tool in $toolsFound) {
    switch ($tool) {
        "claude-desktop" {
            $confirm = Read-Host "`nConfigure GitHub MCP for Claude Desktop? [Y/n]"
            if ($confirm -ne 'n' -and $confirm -ne 'N') {
                Configure-McpTool -configPath $claudeDesktopConfig -toolName "Claude Desktop"
                Write-Warn "Restart Claude Desktop for changes to take effect"
            }
        }
        "claude-code" {
            $confirm = Read-Host "`nConfigure GitHub MCP for Claude Code? [Y/n]"
            if ($confirm -ne 'n' -and $confirm -ne 'N') {
                Configure-McpTool -configPath $claudeCodeConfig -toolName "Claude Code"
            }
        }
        "cursor" {
            Write-Host ""
            Write-Warn "Cursor detected but requires manual MCP config."
            Print-ManualConfig
        }
        "vscode" {
            Write-Host ""
            Write-Warn "VS Code detected but requires manual MCP config."
            Print-ManualConfig
        }
        "manual" {
            Print-ManualConfig
        }
    }
}

# ─── Step 6: Save to user environment (optional) ────────────────────────────
Write-Step "Step 6: Save token to user environment (optional)"

Write-Host ""
Write-Host "Save the token as a permanent user environment variable?"
Write-Host "This makes it available to all terminal sessions and tools."
$saveEnv = Read-Host "Save to user environment? [y/N]"

if ($saveEnv -eq 'y' -or $saveEnv -eq 'Y') {
    $existing = [Environment]::GetEnvironmentVariable("GITHUB_PERSONAL_ACCESS_TOKEN", "User")
    if ($existing) {
        Write-Warn "GITHUB_PERSONAL_ACCESS_TOKEN already set. Skipping."
    } else {
        [Environment]::SetEnvironmentVariable("GITHUB_PERSONAL_ACCESS_TOKEN", $githubPatPlain, "User")
        Write-Ok "Saved to user environment. Restart terminal to activate."
    }
} else {
    Write-Host "[INFO] Skipped. Token is in MCP config only." -ForegroundColor Blue
}

# ─── Done ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   Setup Complete!                            ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  What you can now do in Claude/Cursor:"
Write-Host ""
Write-Host "    'Create an issue on my-org/my-repo for the login bug'"
Write-Host "    'List open PRs on my-org/my-repo'"
Write-Host "    'Read the README from my-org/my-repo'"
Write-Host ""
Write-Host "  Remember: Restart your AI tool for changes to take effect." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Also try Context Bharat for Indian API docs:" -ForegroundColor Cyan
Write-Host "    powershell -File tools\setup-contextbharat-mcp.ps1"
Write-Host ""
Write-Host "  Troubleshooting:"
Write-Host "    - 'spawn npx ENOENT'? This script uses cmd /c npx which fixes it."
Write-Host "    - Token expired?      Re-run this script with a new token"
Write-Host "    - Org access denied?  Ask org admin at: https://github.com/settings/tokens"
Write-Host ""
