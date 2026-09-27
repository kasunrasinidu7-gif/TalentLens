import { SearchForm } from '../components/search-form';

export default function HomePage() {
  return (
    <section className="home-page">
      <div className="shell hero-grid">
        <div className="hero-copy">
          <p className="eyebrow"><span className="status-dot" /> Natural-language scouting engine</p>
          <h1>Find the right player for your team</h1>
          <p className="hero-lede">Search the connected player database using natural-language scouting requests.</p>
          <SearchForm />
        </div>
      </div>
    </section>
  );
}
