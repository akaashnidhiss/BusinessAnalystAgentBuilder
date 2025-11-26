export const API_BASE = (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000";

export const DEFAULT_USER_ID =
  (import.meta as any).env?.VITE_USER_ID || "demo";

export function apiUrl(path: string): string {
  if (path.startsWith("http")) return path;
  const trimmed = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${trimmed}`;
}

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path));
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GET ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}
