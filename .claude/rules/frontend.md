---
globs: ["frontend/**/*.tsx", "frontend/**/*.ts"]
---

# Frontend Rules (Next.js 15)

You are working on the Context7 India marketing site and dashboard.

## Architecture
- Default to Server Components — only use `"use client"` for interactive components
- App Router only — no Pages Router patterns
- Supabase for auth and data — import from `@/lib/supabase`
- Backend API calls via `@/lib/api.ts` — never fetch backend directly from components

## Styling
- Tailwind CSS only — no inline styles except for dynamic values
- Dark mode first (site uses dark theme)
- Brand colors: `#f59e1c` (saffron), `#0f6e56` (teal), `#05080f` (background)

## Always
- Add `export const metadata` to page.tsx files (SEO)
- Handle loading states with Suspense
- Handle error states with error.tsx

## Never
- Use `getServerSideProps` or `getStaticProps` (App Router only)
- Hardcode API keys or secrets
- Use inline `fetch()` in components — use `@/lib/api.ts`
