import { describe, it, expect, vi } from "vitest";
import { resolveLibraryIdHandler, resolveLibraryIdSchema } from "./resolve-library-id.js";

describe("resolve-library-id", () => {
  it("schema validates correctly", () => {
    const valid = { query: "razorpay payment link", libraryName: "razorpay" };
    expect(() => resolveLibraryIdSchema.parse(valid)).not.toThrow();
  });

  it("schema rejects missing libraryName", () => {
    expect(() => resolveLibraryIdSchema.parse({ query: "test" })).toThrow();
  });
});
