import { PlayerDetails, SearchResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

async function apiRequest<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: 'no-store' });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function searchPlayers(query: string, page = 1, pageSize = 8) {
  const params = new URLSearchParams({ q: query, page: String(page), page_size: String(pageSize) });
  return apiRequest<SearchResponse>(`/api/search?${params.toString()}`);
}

export function getPlayer(playerId: string) {
  return apiRequest<PlayerDetails>(`/api/players/${encodeURIComponent(playerId)}`);
}
