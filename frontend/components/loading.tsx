export function Loading({ label = 'Loading player data...' }: { label?: string }) {
  return <div className="loading-state"><span className="spinner" />{label}</div>;
}
