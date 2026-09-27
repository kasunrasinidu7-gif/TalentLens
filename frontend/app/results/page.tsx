'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loading } from '../../components/loading';
import { Pagination } from '../../components/pagination';
import { PlayerCard } from '../../components/player-card';
import { searchPlayers } from '../../lib/api';
import { SearchResponse } from '../../lib/types';

function ResultsPageContent() {
  const router = useRouter();
  const params = useSearchParams();
  const query = params.get('query') || '';
  const page = Math.max(1, Number(params.get('page') || 1));
  const [data, setData] = useState<SearchResponse | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!query) return;
    setData(null);
    setError('');
    searchPlayers(query, page).then(setData).catch((reason) => setError(reason instanceof Error ? reason.message : 'Unable to load player data.'));
  }, [query, page]);

  function changePage(nextPage: number) {
    router.push(`/results?query=${encodeURIComponent(query)}&page=${nextPage}`);
  }

  if (!query) return <section className="shell page-section"><EmptyState title="Start with a scouting request" text="Return to Scout search and describe the player profile you need." action="Back to search" onClick={() => router.push('/')} /></section>;

  return (
    <section className="shell page-section">
      <div className="page-heading"><div><p className="eyebrow">Scout search</p><h1>Players matching your request</h1><p className="query-display">“{query}”</p></div><button className="button button-secondary" onClick={() => router.push('/')}>New search</button></div>
      {data && <div className="result-summary"><span>{data.total} ranked profiles</span><span className="data-badge">{data.data_mode === 'api' ? 'Live API data' : 'Demo data'}</span>{data.model && <span className="data-badge">AI matcher trained on {data.model.training_samples} profiles</span>}<span>Page {data.page}</span></div>}
      {error && <EmptyState title="The search could not be completed" text={error} action="Try again" onClick={() => router.refresh()} />}
      {!data && !error && <Loading />}
      {data && data.players.length === 0 && <EmptyState title="No players matched" text="Try a broader role, age range, or skill description." action="New search" onClick={() => router.push('/')} />}
      {data && data.players.length > 0 && <><div className="player-grid">{data.players.map((player) => <PlayerCard key={player.player_id} player={player} query={query} />)}</div><Pagination page={data.page} hasNext={data.has_next} onPageChange={changePage} /></>}
    </section>
  );
}

export default function ResultsPage() {
  return <Suspense fallback={<section className="shell page-section"><Loading /></section>}><ResultsPageContent /></Suspense>;
}

function EmptyState({ title, text, action, onClick }: { title: string; text: string; action: string; onClick: () => void }) {
  return <div className="empty-state"><h2>{title}</h2><p>{text}</p><button className="button button-primary" onClick={onClick}>{action}</button></div>;
}
