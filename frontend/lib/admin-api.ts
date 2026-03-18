/**
 * Admin API client for the Context Bharat backend.
 * Authenticates using an admin key stored in localStorage.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.contextbharat.com";

const STORAGE_KEY = "contextbharat_admin_key";

export function getAdminKey(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem(STORAGE_KEY) || "";
}

export function setAdminKey(key: string): void {
  localStorage.setItem(STORAGE_KEY, key);
}

export function clearAdminKey(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export async function adminFetch<T = unknown>(path: string, options?: RequestInit): Promise<T> {
  const key = getAdminKey();
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...options?.headers,
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error(`Admin API error: ${res.status}`);
  return res.json();
}
