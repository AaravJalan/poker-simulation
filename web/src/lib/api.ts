/**
 * API base URL. Empty = same origin (works with Vite proxy in dev).
 * Set VITE_API_URL=http://localhost:8000 for preview or when proxy isn't used.
 */
export const API_BASE = (import.meta.env.VITE_API_URL as string) || ''

export function apiUrl(path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE}${p}`
}
