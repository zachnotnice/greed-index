import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Greed Index — Holding Billionaires Accountable",
  description:
    "A public leaderboard ranking America's top billionaires by genuine charitable giving. " +
    "Who's giving back — and who's just hoarding? Data-driven. Transparent. Updated regularly.",
  openGraph: {
    title: "Greed Index",
    description: "America's 200 richest people, ranked by how much they actually give back.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0a0a0a] text-white">
        <nav className="border-b border-white/10 bg-black/40 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-14">
              <a href="/" className="flex items-center gap-2">
                <span className="text-2xl">💰</span>
                <span className="font-bold text-lg tracking-tight">
                  Greed<span className="text-red-500">Index</span>
                </span>
              </a>
              <div className="flex items-center gap-6 text-sm text-white/60">
                <a href="/" className="hover:text-white transition-colors">Leaderboard</a>
                <a href="/methodology" className="hover:text-white transition-colors">Methodology</a>
                <a href="/about" className="hover:text-white transition-colors">About</a>
              </div>
            </div>
          </div>
        </nav>
        {children}
        <footer className="border-t border-white/10 mt-24 py-8 text-center text-white/30 text-sm">
          <p>GreedIndex — Data sourced from IRS Form 990 filings, Forbes, and public records.</p>
          <p className="mt-1">Not affiliated with any political organization. Methodology is fully transparent.</p>
        </footer>
      </body>
    </html>
  );
}
