export function Pagination({ page, hasNext, onPageChange }: { page: number; hasNext: boolean; onPageChange: (page: number) => void }) {
  return (
    <nav className="pagination" aria-label="Search result pages">
      <button className="button button-secondary" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Previous</button>
      <span>Page {page}</span>
      <button className="button button-secondary" disabled={!hasNext} onClick={() => onPageChange(page + 1)}>Next</button>
    </nav>
  );
}
