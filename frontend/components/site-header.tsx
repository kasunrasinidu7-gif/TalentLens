import Link from 'next/link';

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="shell header-inner">
        <Link href="/" className="brand" aria-label="TalentLens home">
          <span className="brand-mark">TL</span>
          <span>TALENTLENS</span>
        </Link>
        <nav className="main-nav" aria-label="Primary navigation">
          <Link className="nav-active" href="/">Scout Search</Link>
          <Link href="#about">About</Link>
        </nav>
      </div>
    </header>
  );
}
