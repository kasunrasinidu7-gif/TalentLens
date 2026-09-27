'use client';

import { Suspense, useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { InitialsAvatar } from '../../../components/initials-avatar';
import { Loading } from '../../../components/loading';
import { getPlayer } from '../../../lib/api';
import { PlayerDetails } from '../../../lib/types';

function display(value: string | number | null | undefined) { return value === null || value === undefined || value === '' || value === 0 ? 'Unavailable' : String(value); }
function money(value: number) { return value ? `EUR ${(value / 1000000).toFixed(1)}M` : 'Unavailable'; }

function PlayerPageContent() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [player, setPlayer] = useState<PlayerDetails | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    getPlayer(id).then(setPlayer).catch((reason) => setError(reason instanceof Error ? reason.message : 'Unable to load this player.'));
  }, [id]);

  if (error) return <section className="shell page-section"><div className="empty-state"><h1>Player unavailable</h1><p>{error}</p><button className="button button-primary" onClick={() => router.back()}>Back to results</button></div></section>;
  if (!player) return <section className="shell page-section"><Loading label="Loading player dossier..." /></section>;

  const backHref = searchParams.get('query') ? `/results?query=${encodeURIComponent(searchParams.get('query') || '')}&page=1` : '/';
  return (
    <section className="shell page-section">
      <button className="back-link" onClick={() => router.push(backHref)}>&lt;- Back to results</button>
      <div className="profile-header"><InitialsAvatar name={player.name} large /><div className="profile-title"><p className="eyebrow">Player dossier</p><h1>{player.name}</h1><p>{player.position || 'Position unavailable'} · Age {display(player.age)} · {player.nationality || 'Nationality unavailable'}</p><div className="tag-row"><span className="tag">{player.team || 'Team unavailable'}</span><span className="tag">{player.league || 'League unavailable'}</span><span className="tag">{player.source || 'Unknown source'}</span></div></div><div className="profile-score"><span>Match score</span><strong>{display(player.match_score)}{player.match_score ? '%' : ''}</strong></div></div>
      <div className="profile-grid">
        <section className="detail-panel"><div className="panel-kicker">Core profile</div><div className="detail-list"><Detail label="Estimated value" value={money(player.market_value)} /><Detail label="Potential" value={display(player.potential)} /><Detail label="Preferred foot" value={player.foot || 'Unavailable'} /><Detail label="Last updated" value={player.last_updated || 'Unavailable'} /></div></section>
        <section className="detail-panel"><div className="panel-kicker">Performance snapshot</div><div className="detail-list"><Detail label="Appearances" value={display(player.appearances)} /><Detail label="Minutes" value={display(player.minutes)} /><Detail label="Goals" value={display(player.goals)} /><Detail label="Assists" value={display(player.assists)} /></div></section>
      </div>
      <div className="profile-grid profile-grid-wide"><section className="detail-panel"><div className="panel-kicker">Strengths from available data</div>{player.strengths.length ? <div className="strength-list">{player.strengths.map((strength) => <div className="strength" key={strength.label}><span>{strength.label}</span><strong>{strength.value}</strong></div>)}</div> : <p className="muted">No strength metrics were supplied by the current data source.</p>}</section><section className="detail-panel"><div className="panel-kicker">Areas to verify</div><ul className="plain-list">{player.areas_for_improvement.map((item) => <li key={item}>{item}</li>)}</ul></section></div>
      <p className="data-note">{player.message}</p>
    </section>
  );
}

export default function PlayerPage() {
  return <Suspense fallback={<section className="shell page-section"><Loading label="Loading player dossier..." /></section>}><PlayerPageContent /></Suspense>;
}

function Detail({ label, value }: { label: string; value: string }) { return <div><span>{label}</span><strong>{value}</strong></div>; }
