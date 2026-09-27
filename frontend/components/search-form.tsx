'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

const examples = [
  'Young right winger with good speed and crossing',
  'U21 box-to-box midfielder with high passing',
  'Left-footed centre back under EUR 15M',
];

export function SearchForm() {
  const router = useRouter();
  const [query, setQuery] = useState(examples[0]);

  function submit(event: FormEvent) {
    event.preventDefault();
    const cleanQuery = query.trim();
    if (cleanQuery.length >= 2) router.push(`/results?query=${encodeURIComponent(cleanQuery)}&page=1`);
  }

  return (
    <form className="search-form" onSubmit={submit}>
      <label htmlFor="scout-query">Describe the player you want to find</label>
      <div className="search-row">
        <input id="scout-query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="e.g. young right winger with pace and crossing" />
        <button className="button button-primary" type="submit">Find players <span aria-hidden="true">-&gt;</span></button>
      </div>
      <div className="example-row" aria-label="Example scouting searches">
        {examples.map((example) => <button type="button" key={example} onClick={() => setQuery(example)}>{example}</button>)}
      </div>
    </form>
  );
}
