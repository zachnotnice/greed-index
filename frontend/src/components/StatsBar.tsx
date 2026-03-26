import { Stats } from "@/lib/api";

interface StatsBarProps {
  stats: Stats;
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
      <div className="text-2xl font-black text-white font-mono">{value}</div>
      <div className="text-white/40 text-xs mt-1">{label}</div>
      {sub && <div className="text-white/25 text-xs">{sub}</div>}
    </div>
  );
}

export default function StatsBar({ stats }: StatsBarProps) {
  const loopholePct = stats.total_genuine_giving_billions + stats.total_loophole_giving_billions > 0
    ? ((stats.total_loophole_giving_billions / (stats.total_genuine_giving_billions + stats.total_loophole_giving_billions)) * 100).toFixed(0)
    : "0";

  const pledgeFulfillRate = stats.giving_pledge_signatories > 0
    ? ((stats.giving_pledge_fulfilled / stats.giving_pledge_signatories) * 100).toFixed(0)
    : "0";

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <StatCard
        label="Total Net Worth"
        value={`$${stats.total_net_worth_billions.toFixed(0)}B`}
        sub="combined"
      />
      <StatCard
        label="Genuine Giving"
        value={`$${stats.total_genuine_giving_billions.toFixed(1)}B`}
        sub="after loopholes"
      />
      <StatCard
        label="Loophole Amount"
        value={`$${stats.total_loophole_giving_billions.toFixed(1)}B`}
        sub={`${loopholePct}% of claimed giving`}
      />
      <StatCard
        label="Avg Giving Ratio"
        value={`${stats.average_giving_ratio_pct.toFixed(3)}%`}
        sub="of net worth"
      />
      <StatCard
        label="Pledge Signatories"
        value={`${stats.giving_pledge_signatories}`}
        sub={`${stats.giving_pledge_fulfilled} actually followed through`}
      />
      <StatCard
        label="Pledge Fulfillment"
        value={`${pledgeFulfillRate}%`}
        sub="of signatories gave"
      />
    </div>
  );
}
