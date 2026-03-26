import { api, BillionaireListItem, Stats } from "@/lib/api";
import LeaderboardTable from "@/components/LeaderboardTable";
import StatsBar from "@/components/StatsBar";

export const revalidate = 300; // revalidate every 5 minutes

async function getData() {
  try {
    const [leaderboard, stats] = await Promise.all([
      api.getLeaderboard({ limit: 200 }),
      api.getStats(),
    ]);
    return { leaderboard, stats };
  } catch {
    return { leaderboard: null, stats: null };
  }
}

export default async function HomePage() {
  const { leaderboard, stats } = await getData();

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 bg-red-950/40 border border-red-800/40 rounded-full px-4 py-1.5 text-red-400 text-sm mb-6">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          Updated weekly from IRS 990 filings & public records
        </div>
        <h1 className="text-5xl sm:text-6xl font-black tracking-tight mb-4">
          The{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-red-800">
            Greed Index
          </span>
        </h1>
        <p className="text-white/50 text-lg max-w-2xl mx-auto">
          America&apos;s 200 wealthiest people, ranked by how much they actually give back —{" "}
          <span className="text-white/70">after filtering out tax loopholes, vanity gifts, and empty pledges.</span>
        </p>
        <p className="text-white/30 text-sm mt-3 max-w-xl mx-auto">
          Higher score = more greedy. Scores account for DAFs with no payout, charitable LLCs,
          naming rights deals, and conservation easement abuse.
        </p>
      </div>

      {/* Stats Bar */}
      {stats && <StatsBar stats={stats} />}

      {/* Leaderboard */}
      <div className="mt-8">
        <LeaderboardTable
          billionaires={leaderboard?.billionaires ?? []}
          total={leaderboard?.total ?? 0}
          lastUpdated={leaderboard?.last_updated ?? null}
        />
      </div>

      {/* Call to action */}
      <div className="mt-16 grid sm:grid-cols-2 gap-6">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-2">Why This Matters</h2>
          <p className="text-white/50 text-sm leading-relaxed">
            The 200 wealthiest Americans hold more wealth than the bottom 60% of the country combined.
            While many publicly celebrate &quot;giving back,&quot; the reality is often donor-advised funds that
            sit for decades, charitable LLCs with no transparency, or vanity building names at elite universities.
            This index cuts through the PR.
          </p>
        </div>
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-2">How Scores Are Calculated</h2>
          <p className="text-white/50 text-sm leading-relaxed">
            Each donation is classified by type and evaluated for loophole status. Genuine giving as a
            percentage of net worth determines the base score. We add penalties for wealth growing faster
            than giving, and bonuses for high-impact cause areas. The full methodology is{" "}
            <a href="/methodology" className="text-red-400 hover:text-red-300 underline">
              publicly documented
            </a>
            .
          </p>
        </div>
      </div>
    </main>
  );
}
