/**
 * Context7 India TypeScript SDK
 * Programmatic access to the documentation API.
 *
 * Usage:
 * ```typescript
 * import { Context7IndiaClient } from "@context7india/sdk";
 * const client = new Context7IndiaClient({ apiKey: "c7i_..." });
 * const docs = await client.queryDocs({ libraryId: "/razorpay/razorpay-sdk", query: "payment link" });
 * ```
 */
export { Context7IndiaClient } from "./client.js";
export type { ClientOptions, QueryDocsParams, QueryDocsResult, Library } from "./types.js";
