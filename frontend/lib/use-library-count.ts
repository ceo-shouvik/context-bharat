/**
 * React hook to fetch the total library count from the API.
 * Falls back to null if the API is unreachable.
 */
"use client";

import { useEffect, useState } from "react";
import { getLibraryCount } from "@/lib/api";

/** Cached count so we only fetch once per page session.
 *  Seeded with 100 to avoid flash of empty text on first render. */
let cachedCount: number | null = 120;

export function useLibraryCount(): number | null {
  const [count, setCount] = useState<number | null>(cachedCount);

  useEffect(() => {
    if (cachedCount !== null) return;
    getLibraryCount().then((n) => {
      if (n !== null) {
        cachedCount = n;
        setCount(n);
      }
    });
  }, []);

  return count;
}

/**
 * Format the library count for display.
 * If count is available, shows e.g. "75+" or "120+".
 * If null (API unreachable), returns the fallback string.
 */
export function formatLibraryCount(count: number | null, fallback = "Indian APIs"): string {
  if (count === null) return fallback;
  return `${count}+`;
}
