/**
 * Context Bharat TypeScript SDK
 * Programmatic access to the documentation API.
 *
 * Usage:
 * ```typescript
 * import { ContextBharatClient } from "@contextbharat/sdk";
 * const client = new ContextBharatClient({ apiKey: "cb_..." });
 * const docs = await client.queryDocs({ libraryId: "/razorpay/razorpay-sdk", query: "payment link" });
 * ```
 */
export { ContextBharatClient } from "./client.js";
export type { ClientOptions, QueryDocsParams, QueryDocsResult, Library } from "./types.js";
