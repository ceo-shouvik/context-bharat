/**
 * LibraryCountBadge — client component that fetches and displays
 * the real library count from the API. Falls back gracefully.
 */
"use client";

import { useLibraryCount, formatLibraryCount } from "@/lib/use-library-count";

interface Props {
  /** Text appended after the count, e.g. " libraries indexed" */
  suffix?: string;
  /** Shown when API is unreachable */
  fallback?: string;
}

export function LibraryCountBadge({ suffix = "", fallback = "Indian APIs" }: Props) {
  const count = useLibraryCount();
  const display = formatLibraryCount(count, fallback);
  return <>{display}{suffix}</>;
}
