---
globs: ["mcp-server/**/*.ts"]
---

# MCP Server Rules (TypeScript)

You are working on the Context Bharat MCP server.

## This is the developer-facing layer
Every output from this server is consumed by an LLM (Claude, GPT-4, etc.).
Format responses as clean Markdown that an LLM can easily parse.

## Always
- Use Zod for input validation on all tool inputs
- Export handler functions separately from tool definitions (enables unit testing)
- Type everything — no `any`
- Handle BackendError explicitly (404 = library not found, not a crash)
- Test tool schemas with vitest

## MCP tool output format
```typescript
// Preferred: structured Markdown
return `## ${libraryName} Documentation\n\n${docs}\n\n---\n**Sources:** ${sources}`;

// Never: raw JSON objects (LLMs struggle with these)
// Never: HTML (markdown is cleaner)
```

## Adding a new tool
1. Create `src/tools/my-tool.ts` with schema + handler
2. Export and register in `src/index.ts`
3. Add test in `src/tools/my-tool.test.ts`
4. Update `ListToolsRequestSchema` handler

## Build and test
```bash
pnpm build     # Compile TypeScript
pnpm test      # Run vitest
pnpm inspect   # Open MCP inspector for manual testing
```
