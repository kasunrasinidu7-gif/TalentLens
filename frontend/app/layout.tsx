import type { Metadata } from 'next';
import './globals.css';
import { SiteHeader } from '../components/site-header';

export const metadata: Metadata = {
  title: 'TalentLens | Football Scouting Intelligence',
  description: 'Natural-language football player search and transparent recruitment analysis.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <SiteHeader />
        <main>{children}</main>
      </body>
    </html>
  );
}
