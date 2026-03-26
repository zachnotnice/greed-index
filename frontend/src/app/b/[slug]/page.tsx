import { api, BillionaireDetail } from "@/lib/api";
import { notFound } from "next/navigation";
import { Metadata } from "next";
import Link from "next/link";
import GreedMeter, { getTier, getScoreColor } from "@/components/GreedMeter";
import DonationTypeTag from "@/components/DonationTypeTag";
import WealthClock from "@/components/WealthClock";
import ImpactCalculator from "@/components/ImpactCalculator";
import MoveUpSimulator from "@/components/MoveUpSimulator";
import clsx from "clsx";

export const revalidate = 300;

interface Props {
  params: { slug: string };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const b = await api.getBillionaire(params.slug);
    const score = b.latest_score?.score ?? 50;
    const tier = getTier(score);
    return {
      title: `${b.name} — Greed Score ${score.toFixed(1)} (${tier.label}) | Greed Index`,
      description: `${b.name} has a Greed Score of ${score.toFixed(1)} (rank #${b.greed_rank ?? "?"}). Net worth: $${b.net_worth_billions}B. Genuine giving: $${(b.adjusted_giving_billions ?? 0).toFixed(2)}B. ${b.bio_blurb?.slice(0, 120) ?? ""}`,
    };
  } catch {
    return { title: "Billionaire Profile | Greed Index" };
  }
}

export default async function BillionairePage({ params }: Props) {
  let b: BillionaireDetail;
  try {
    b = await api.getBillionaire(params.slug);
  } catch {
    notFound();
  }

  const score = b.latest_score?.score ?? 50;
  const tier = getTier(score);
  const color = getScoreColor(score);
  const breakdown = b.latest_score?.score_breakdown as Record<string, unknown> | null;
  const donationBreakdown = (breakdown?.donation_breakdown as Array<Record<string, unknown>>) ?? [];

  const totalClaimed = b.latest_score?.total_giving_claimed_billions ?? 0;
  const totalGenuine = b.latest_score?.adjusted_giving_billions ?? 0;
  const totalLoophole = b.latest_score?.loophole_amount_billions ?? 0;
  const loopholeShare = totalClaimed > 0 ? (totalLoophole / totalClaimed) * 100 : 0;

  const shareText = encodeURIComponent(
    `${b.name} has a Greed Score of ${score.toFixed(1)}/100 on GreedIndex — ranking #${b.greed_rank} among America's wealthiest. Only ${(b.giving_ratio_pct ?? 0).toFixed(3)}% of their net worth goes to genuine charity. #GreedIndex`
  );

  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back */}
      <Link href="/" className="text-white/40 hover:text-white text-sm transition-colors mb-6 inline-flex items-center gap-1">
        ← Back to Leaderboard
      </Link>

      {/* Header */}
      <div className="bg-gradient-to-br from-white/5 to-transparent border border-white/10 rounded-2xl p-8 mb-8">
        <div className="flex flex-col sm:flex-row gap-6 items-start">
          {/* Name & basic info */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="bg-white/10 border border-white/20 rounded-xl px-3 py-1 font-mono font-bold text-2xl">
                #{b.greed_rank ?? "—"}
              </span>
              <span className={clsx("text-lg font-semibold", tier.color)}>{tier.label}</span>
            </div>
            <h1 className="text-4xl font-black tracking-tight mb-1">{b.name}</h1>
            <p className="text-white/40">{b.wealth_source} · {b.industry}</p>
            {b.birth_year && (
              <p className="text-white/25 text-sm">Born {b.birth_year} · Age {new Date().getFullYear() - b.birth_year}</p>
            )}

            {/* Pledge badges */}
            <div className="flex gap-2 mt-3">
              {b.giving_pledge_signed && (
                <span className={clsx(
                  "text-sm px-3 py-1 rounded-lg border",
                  b.giving_pledge_fulfilled
                    ? "bg-green-900/30 text-green-400 border-green-700/30"
                    : "bg-yellow-900/30 text-yellow-500 border-yellow-700/30"
                )}>
                  {b.giving_pledge_fulfilled
                    ? "✓ Giving Pledge — honored"
                    : "⚠ Giving Pledge signed — not yet honored"}
                </span>
              )}
              {!b.giving_pledge_signed && (
                <span className="text-sm px-3 py-1 rounded-lg border border-white/10 text-white/30">
                  Has not signed the Giving Pledge
                </span>
              )}
              {b.twitter_handle && (
                <a
                  href={`https://twitter.com/${b.twitter_handle}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm px-3 py-1 rounded-lg border border-white/10 text-white/40 hover:text-white/70 transition-colors"
                >
                  @{b.twitter_handle}
                </a>
              )}
            </div>
          </div>

          {/* Big score */}
          <div className="text-center sm:text-right">
            <div className="text-7xl font-black font-mono mb-1" style={{ color }}>
              {score.toFixed(1)}
            </div>
            <div className="text-white/40 text-sm mb-3">Greed Score / 100</div>
            <GreedMeter score={score} size="lg" />
          </div>
        </div>

        {/* Bio */}
        {b.bio_blurb && (
          <p className="mt-6 text-white/50 text-sm leading-relaxed border-t border-white/10 pt-6">
            {b.bio_blurb}
          </p>
        )}
      </div>

      {/* Key numbers */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
          <div className="text-2xl font-black font-mono text-white">${b.net_worth_billions.toFixed(1)}B</div>
          <div className="text-white/40 text-xs mt-1">Net Worth</div>
        </div>
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
          <div className="text-2xl font-black font-mono text-green-400">${totalGenuine.toFixed(2)}B</div>
          <div className="text-white/40 text-xs mt-1">Genuine Giving</div>
        </div>
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
          <div className="text-2xl font-black font-mono text-orange-400">${totalLoophole.toFixed(2)}B</div>
          <div className="text-white/40 text-xs mt-1">Loophole Amount</div>
          {loopholeShare > 0 && (
            <div className="text-white/25 text-xs">{loopholeShare.toFixed(0)}% of claimed</div>
          )}
        </div>
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
          <div className="text-2xl font-black font-mono text-white/70">
            {(b.giving_ratio_pct ?? 0).toFixed(3)}%
          </div>
          <div className="text-white/40 text-xs mt-1">Genuine Giving Ratio</div>
          <div className="text-white/25 text-xs">of net worth</div>
        </div>
      </div>

      {/* Greed Clock */}
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-3">Wealth Accumulation Clock</h2>
        <WealthClock
          wealthPerSecond={b.wealth_per_second}
          name={b.name}
        />
      </div>

      {/* Donations breakdown */}
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Giving Record</h2>
        {b.donations.length === 0 ? (
          <div className="bg-red-950/20 border border-red-800/30 rounded-xl p-6 text-center text-red-300">
            No documented charitable giving on record.
          </div>
        ) : (
          <div className="space-y-3">
            {b.donations.map((d, i) => (
              <div
                key={d.id}
                className={clsx(
                  "border rounded-xl p-4",
                  d.is_loophole
                    ? "border-orange-800/30 bg-orange-950/10"
                    : "border-white/10 bg-white/5"
                )}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-sm">{d.organization_name}</span>
                      {d.year && <span className="text-white/30 text-xs">{d.year}</span>}
                      <DonationTypeTag type={d.donation_type} />
                      {!d.verified && (
                        <span className="text-xs px-1.5 py-0.5 rounded border border-yellow-700/30 text-yellow-500 bg-yellow-900/20">
                          Estimated
                        </span>
                      )}
                    </div>
                    {d.is_loophole && d.loophole_reason && (
                      <p className="text-orange-400/70 text-xs mt-2 leading-relaxed">
                        ⚠ {d.loophole_reason}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className={clsx(
                      "font-mono font-bold text-sm",
                      d.is_loophole ? "line-through text-white/30" : "text-white"
                    )}>
                      ${d.amount_billions.toFixed(3)}B
                    </div>
                    {d.is_loophole && (
                      <div className="text-green-400 font-mono text-xs">
                        ${(d.amount_billions * (1 - d.loophole_pct)).toFixed(3)}B genuine
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Score breakdown */}
      {breakdown && (
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4">Score Breakdown</h2>
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3 font-mono text-sm">
            {[
              {
                label: "Giving Component",
                value: breakdown.giving_component as number,
                description: "Based on genuine giving as % of net worth (lower = more generous)",
                weight: "65%",
              },
              {
                label: "Quality Component",
                value: breakdown.quality_component as number,
                description: "Impact of cause categories (global health, poverty score higher)",
                weight: "20%",
              },
              {
                label: "Wealth Growth Penalty",
                value: (breakdown.wealth_penalty as number) * 10,
                description: "Penalty for wealth growing faster than giving",
                weight: "15%",
              },
              ...(breakdown.pledge_penalty as number > 0 ? [{
                label: "Pledge Penalty",
                value: breakdown.pledge_penalty as number,
                description: "Signed Giving Pledge but not followed through",
                weight: "flat",
              }] : []),
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-4">
                <span className="text-white/40 w-40 text-xs">{item.label} ({item.weight})</span>
                <div className="flex-1 bg-white/10 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-red-500 transition-all"
                    style={{ width: `${Math.min(100, item.value)}%` }}
                  />
                </div>
                <span className="text-white/60 w-12 text-right">{(item.value ?? 0).toFixed(1)}</span>
                <span className="text-white/25 text-xs w-32 hidden sm:block">{item.description}</span>
              </div>
            ))}
            <div className="border-t border-white/10 pt-3 flex justify-between text-white">
              <span>Final Greed Score</span>
              <span className="font-bold" style={{ color }}>{score.toFixed(1)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Move Up Simulator */}
      {b.greed_rank && b.greed_rank > 1 && (
        <div className="mb-8">
          <MoveUpSimulator
            slug={b.slug}
            currentRank={b.greed_rank}
            name={b.name}
            netWorthBillions={b.net_worth_billions}
          />
        </div>
      )}

      {/* Impact Calculator */}
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">What Could Their Wealth Do?</h2>
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <ImpactCalculator
            defaultAmount={b.net_worth_billions * 0.01}
            label={`If ${b.name.split(" ")[0]} gave just 1% of their net worth ($${(b.net_worth_billions * 0.01).toFixed(1)}B), it could fund:`}
          />
        </div>
      </div>

      {/* Share */}
      <div className="bg-gradient-to-r from-red-950/30 to-transparent border border-red-800/20 rounded-2xl p-6">
        <h2 className="text-lg font-bold mb-2">Share This Profile</h2>
        <p className="text-white/40 text-sm mb-4">
          Public accountability only works with public attention.
        </p>
        <div className="flex gap-3 flex-wrap">
          <a
            href={`https://twitter.com/intent/tweet?text=${shareText}`}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Share on X (Twitter)
          </a>
          <button
            onClick={() => navigator.clipboard.writeText(window.location.href)}
            className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Copy Link
          </button>
        </div>
      </div>
    </main>
  );
}
