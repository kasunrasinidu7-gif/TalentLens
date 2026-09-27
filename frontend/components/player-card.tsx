import Link from 'next/link';
import { InitialsAvatar } from './initials-avatar';
import { Player } from '../lib/types';

function metric(value: number) { return value ? String(value) : 'Unavailable'; }
function money(value: number) { return value ? `EUR ${(value / 1000000).toFixed(1)}M` : 'Unavailable'; }

export function PlayerCard({ player, query }: { player: Player; query: string }) {
  return (
    <article className="player-card">
      <div className="card-topline"><span className="match-score">{Math.round(player.match_score || 0)}% match</span><span className="source-label">{player.source || 'Unknown source'}</span></div>
      <div className="player-identity"><InitialsAvatar name={player.name} /><div><h2>{player.name}</h2><p>{player.position || 'Position unavailable'} · Age {player.age || 'Unavailable'}</p></div></div>
      <div className="player-meta"><span>{player.nationality || 'Nationality unavailable'}</span><span>{player.team || 'Team unavailable'}</span><span>{player.league || 'League unavailable'}</span></div>
      <p className="reason">{player.reasons[0] || 'Ranked by the current scouting engine.'}</p>
      <div className="metrics-grid"><Metric label="Speed" value={metric(player.speed)} /><Metric label="Crossing" value={metric(player.crossing)} /><Metric label="Potential" value={metric(player.potential)} /><Metric label="Value" value={money(player.market_value)} /></div>
      <Link className="card-link" href={`/player/${encodeURIComponent(player.player_id)}?query=${encodeURIComponent(query)}`}>View player details <span aria-hidden="true">-&gt;</span></Link>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}
