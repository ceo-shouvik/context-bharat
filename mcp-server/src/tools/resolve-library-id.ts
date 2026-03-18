/**
 * MCP Tool: resolve-library-id
 * Maps a human library name to a canonical ContextBharat library ID.
 *
 * Example: "zerodha trading api" → "/zerodha/kite-api"
 */
import { z } from "zod";
import { backendClient, BackendError } from "../client.js";

export const resolveLibraryIdSchema = z.object({
  query: z.string().describe(
    "The full user query or task description. Used to improve resolution accuracy.",
  ),
  libraryName: z.string().describe(
    "The library or API name to resolve. E.g. 'razorpay', 'zerodha kite', 'ondc protocol'.",
  ),
});

export type ResolveLibraryIdInput = z.infer<typeof resolveLibraryIdSchema>;

export async function resolveLibraryIdHandler(
  input: ResolveLibraryIdInput,
): Promise<string> {
  try {
    const result = await backendClient.resolveLibrary({
      query: input.query,
      libraryName: input.libraryName,
    });

    // Format output for LLM consumption
    const lines = [
      `Library resolved: **${result.name}**`,
      `Library ID: \`${result.libraryId}\``,
    ];
    if (result.description) {
      lines.push(`Description: ${result.description}`);
    }
    if (result.tags.length > 0) {
      lines.push(`Tags: ${result.tags.join(", ")}`);
    }
    if (result.versions.length > 0) {
      lines.push(`Versions: ${result.versions.join(", ")}`);
    }
    lines.push(
      `\nUse \`query-docs\` with libraryId: "${result.libraryId}" to retrieve documentation.`,
    );

    return lines.join("\n");
  } catch (error) {
    if (error instanceof BackendError && error.status === 404) {
      return [
        `Library "${input.libraryName}" not found in the Context Bharat index.`,
        ``,
        `Try browsing available libraries at https://contextbharat.com/libraries`,
        `Or contribute a new library: https://github.com/contextbharat/context-bharat/blob/main/docs/CONTRIBUTING.md`,
      ].join("\n");
    }
    throw error;
  }
}
