# @context7india/mcp

MCP server for Indian API documentation.

## Install

```bash
npx @context7india/mcp --api-key YOUR_KEY
```

## Claude Desktop config

```json
{
  "mcpServers": {
    "context7india": {
      "command": "npx",
      "args": ["-y", "@context7india/mcp", "--api-key", "YOUR_KEY"]
    }
  }
}
```

## Development

```bash
pnpm install
pnpm dev          # tsx watch
pnpm build        # Compile to dist/
pnpm test         # vitest
pnpm inspect      # MCP inspector at localhost:5173
```

## Forked from

[upstash/context7](https://github.com/upstash/context7) (MIT License)
