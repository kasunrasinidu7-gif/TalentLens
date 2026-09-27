const API_BASE = window.TALENTLENS_API_BASE || 'http://127.0.0.1:8000';

function cleanEncoding(value) {
  if (typeof value !== 'string') return value;
  const replacements = [
    ['\u00e2\u201a\u00ac', 'EUR'],
    ['\u00e2\u20ac\u0093', '-'],
    ['\u00e2\u20ac\u0094', '-'],
    ['\u00e2\u20ac\u201c', '-'],
    ['\u00e2\u20ac\u201d', '-'],
    ['\u00e2\u20ac\u009c', '"'],
    ['\u00e2\u20ac\u009d', '"'],
    ['\u00e2\u20ac\u00a2', '|'],
    ['\u00e2\u2020\u0092', '->'],
    ['\u00e2\u2020\u2019', '->'],
    ['\u00c2\u2020\u2019', '->'],
    ['\u00c3\u00a9', 'e'],
    ['\u00c2\u00b0', 'deg'],
  ];
  return replacements.reduce((result, [bad, replacement]) => result.split(bad).join(replacement), value);
}

function repairEncodingArtifacts() {
  document.body.innerHTML = cleanEncoding(document.body.innerHTML);
}

function formatValue(value) {
  if (!value) return 'Unavailable';
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(value);
}

function setText(element, value) {
  if (element && value !== undefined && value !== null) element.textContent = cleanEncoding(String(value));
}

function setLabeledMetric(label, value) {
  const labelNode = [...document.querySelectorAll('span')].find((node) => node.textContent.trim() === label);
  const valueNode = labelNode?.parentElement?.querySelector('.font-headline-lg');
  setText(valueNode, value);
}

async function searchPlayers(query) {
  const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}&limit=5`);
  if (!response.ok) throw new Error('Search failed');
  return response.json();
}

async function loadPlayer(playerId) {
  const response = await fetch(`${API_BASE}/api/players/${encodeURIComponent(playerId)}`);
  if (!response.ok) throw new Error('Player details failed');
  return response.json();
}

function connectNavigation() {
  document.querySelectorAll('nav a').forEach((link) => {
    if (link.textContent.includes('Scout Search')) link.href = 'index.html';
  });
  const page = window.location.pathname.split('/').pop() || 'index.html';
  if (page === 'index.html') connectSearchPage();
  if (page === 'results.html') connectResultsPage();
  if (page === 'player.html') connectPlayerPage();
}

function connectSearchPage() {
  const input = document.getElementById('scout-query');
  const search = document.getElementById('search-btn');
  const submit = () => {
    const query = input?.value.trim();
    if (query) window.location.href = 'results.html?query=' + encodeURIComponent(query);
  };
  search?.addEventListener('click', submit);
  input?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') submit();
  });
}

function populateResultCard(card, player, index) {
  const name = card.querySelector('h2');
  setText(name, player.name);
  const match = name?.parentElement?.querySelector('div.flex.items-center.gap-1');
  setText(match, `${Math.round(player.match_score || 0)}% MATCH`);
  const meta = name?.parentElement?.children[1];
  setText(meta, `${player.position || '—'} • Age ${player.age || '—'} • ${player.nationality || '—'} • ${player.team || '—'} • ${player.league || '—'}`);
  setText(card.querySelector('p'), player.reasons?.join('; ') || 'Statistical fit returned by the current scouting engine.');
  const metricValues = card.querySelectorAll('span.font-headline-md');
  setText(metricValues[0], player.speed || '—');
  setText(metricValues[1], player.crossing || '—');
  setText(metricValues[2], player.potential || '—');
  setText(card.querySelector('span.font-headline-lg'), formatValue(player.market_value));
  const button = [...card.querySelectorAll('button')].find((node) => node.textContent.includes('View Details'));
  if (button) button.onclick = () => window.location.href = `player.html?id=${encodeURIComponent(player.player_id)}`;
  setText(card.querySelector('span.absolute'), `#${index + 1}`);
}

async function connectResultsPage() {
  const query = new URLSearchParams(window.location.search).get('query') || 'Find suitable players';
  setText(document.querySelector('p.font-headline-lg'), `“${query}”`);
  try {
    const data = await searchPlayers(query);
    setText(document.querySelector('span.font-headline-xl'), data.count);
    const cards = [...document.querySelectorAll('article')];
    cards.forEach((card, index) => {
      if (data.players[index]) {
        card.style.display = '';
        populateResultCard(card, data.players[index], index);
      } else {
        card.style.display = 'none';
      }
    });
  } catch (error) {
    console.warn('TalentLens API unavailable; showing generated demo results.', error);
  }
}

async function connectPlayerPage() {
  const back = [...document.querySelectorAll('a')].find((link) => link.textContent.includes('Back to Results'));
  if (back) back.href = 'results.html';
  const searchAgain = [...document.querySelectorAll('button')].find((button) => button.textContent.includes('Search Again'));
  if (searchAgain) searchAgain.onclick = () => window.location.href = 'index.html';
  const playerId = new URLSearchParams(window.location.search).get('id');
  if (!playerId) return;
  try {
    const player = await loadPlayer(playerId);
    setText(document.querySelector('h1'), player.name);
    setText(document.querySelector('h1')?.parentElement?.querySelector('p'), `${player.position || '—'} • Age ${player.age || '—'} • ${player.nationality || '—'} • ${player.team || '—'} • ${player.league || '—'}`);
    setLabeledMetric('Estimated Potential', `${player.potential || '—'} / 100`);
    setLabeledMetric('Appearances', player.appearances || '—');
    setLabeledMetric('Minutes Played', player.minutes ? `${player.minutes}'` : '—');
    setLabeledMetric('Goals', player.goals || '—');
    setLabeledMetric('Assists', player.assists || '—');
    setLabeledMetric('Crossing Accuracy', player.crossing ? `${player.crossing}/100` : '—');
    setLabeledMetric('Successful Dribbles', player.dribbling || '—');
    setLabeledMetric('Progressive Passing', player.passing || '—');
  } catch (error) {
    console.warn('TalentLens API unavailable; showing generated demo profile.', error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  repairEncodingArtifacts();
  connectNavigation();
});
