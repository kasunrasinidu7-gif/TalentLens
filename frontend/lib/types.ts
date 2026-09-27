export interface Player {
  player_id: string;
  name: string;
  age: number | null;
  position: string | null;
  nationality: string | null;
  team: string | null;
  league: string | null;
  foot: string | null;
  speed: number;
  crossing: number;
  dribbling: number;
  passing: number;
  finishing: number;
  defending: number;
  physicality: number;
  appearances: number;
  minutes: number;
  goals: number;
  assists: number;
  market_value: number;
  potential: number;
  source: string;
  last_updated: string | null;
  match_score: number | null;
  reasons: string[];
}

export interface SearchResponse {
  query: string;
  data_mode: 'api' | 'demo';
  model?: { version: string; type: string; training_samples: number; trained: boolean };
  page: number;
  page_size: number;
  total: number;
  has_next: boolean;
  count: number;
  players: Player[];
}

export interface PlayerDetails extends Player {
  strengths: { label: string; value: number }[];
  areas_for_improvement: string[];
  league_readiness: number;
  value_history: { date: string; value: number }[];
  message: string;
}
