/**
 * MCP Tool: query-docs
 * Retrieves relevant documentation for a library + query.
 *
 * Supports:
 * - Indian fintech APIs (Razorpay, Cashfree, Zerodha, ...)
 * - India Stack / DPI (ONDC, UPI, GSTN, DigiLocker, ...)
 * - Global frameworks (React, Next.js, FastAPI, ...)
 * - Hindi and regional language docs (language parameter)
 */
import { z } from "zod";
import { backendClient, BackendError } from "../client.js";

export const SUPPORTED_LANGUAGES = ["en", "hi", "ta", "te", "kn", "bn"] as const;
type Language = (typeof SUPPORTED_LANGUAGES)[number];

export const queryDocsSchema = z.object({
  libraryId: z
    .string()
    .describe(
      "ContextBharat-compatible library ID. Use resolve-library-id first if you only have a name. " +
      "Format: /owner/repo — e.g. /razorpay/razorpay-sdk, /zerodha/kite-api, /ondc/protocol-specs",
    ),
  query: z
    .string()
    .describe(
      "The developer's specific question or task. Be specific for better results. " +
      "E.g. 'create a payment link with expiry' not just 'payment'.",
    ),
  tokenBudget: z
    .number()
    .min(100)
    .max(20000)
    .default(5000)
    .describe(
      "Maximum number of tokens in the response. Default 5000. " +
      "Increase for comprehensive guides, decrease for quick references.",
    ),
  language: z
    .enum(SUPPORTED_LANGUAGES)
    .default("en")
    .describe(
      "Documentation language. 'hi' for Hindi, 'ta' for Tamil, 'te' for Telugu. " +
      "Hindi available for top Indian APIs.",
    ),
});

export type QueryDocsInput = z.infer<typeof queryDocsSchema>;

export async function queryDocsHandler(input: QueryDocsInput): Promise<string> {
  try {
    const result = await backendClient.queryDocs({
      libraryId: input.libraryId,
      query: input.query,
      tokenBudget: input.tokenBudget,
      language: input.language,
    });

    // Build formatted response
    const parts: string[] = [];

    // Header with freshness info
    const freshnessNote =
      result.freshnessScore !== undefined && result.freshnessScore < 0.5
        ? ` ⚠️ Note: These docs may be stale (freshness: ${(result.freshnessScore * 100).toFixed(0)}%)`
        : "";
    parts.push(`## ${result.libraryName} Documentation${freshnessNote}\n`);

    // Main content
    parts.push(result.docs);

    // Sources
    if (result.sources.length > 0) {
      parts.push(`\n---\n**Sources:** ${result.sources.map(s => `[${s}](${s})`).join(" · ")}`);
    }

    return parts.join("\n");
  } catch (error) {
    if (error instanceof BackendError && error.status === 404) {
      return [
        `Library \`${input.libraryId}\` not found or not yet indexed.`,
        ``,
        `Check the full library catalog: https://contextbharat.com/libraries`,
        `If this library should be indexed, open an issue: https://github.com/contextbharat/context-bharat/issues`,
      ].join("\n");
    }
    throw error;
  }
}
