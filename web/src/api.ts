const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} on ${path}`);
  }
  return res.json() as Promise<T>;
}

export const CURRENT_SEASON = 2025;
