"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { BillionaireListItem } from "@/lib/api";
import GreedMeter, { getScoreColor, getTier } from "./GreedMeter";
import clsx from "clsx";

interface LeaderboardTableProps {
  billionaires: BillionaireListItem[];
  total: number;
  lastUpdated: string | null;
}

const INDUSTRIES = ["All", "Technology", "Finance", "Retail", "Energy", "Media", "Consumer Goods", "Philanthropy"];

export default function LeaderboardTable({ billionaires, total, lastUpdated }: LeaderboardTableProps) {
  const [search, setSearch] = useState("");
  const [industryFilter, setIndustryFilter] = useState("All");
  const [sortBy, setSortBy] = useState<"greed" | "net_worth" | "giving_ratio">("greed");

  const filtered = billionaires
    .filter((b) => {
      const matchSearch = b.name.toLowerCase().includes(search.toLowerCase()) ||
        b.wealth_source.toLowerCase().includes(search.toLowerCase());
      const matchIndustry = industryFilter === "All" ||
        b.industry.toLowerCase().includes(industryFilter.toLowerCase());
      return matchSearch && matchIndustry;
    })
    .sort((a, b) => {
      if (sortBy === "greed") return (a.greed_rank ?? 999) - (b.greed_rank ?? 999);
      if (sortBy === "net_worth") return b.net_worth_billions - a.net_worth_billions;
      if (sortBy === "giving_ratio") return (a.giving_ratio_pct ?? 0) - (b.giving_ratio_pct ?? 0);
      return 0;
    });

  const getRankBadge = (rank: number | null) => {
    if (!rank) return null;
    if (rank === 1) return "bg-red-800/80 border-red-600 text-red-200";
    if (rank <= 5) return "bg-red-900/60 border-red-700/60 text-red-300";
    if (rank <= 20) return "bg-orange-900/40 border-orange-700/40 text-orange-300";
    return "bg-white/5 border-white/10 text-white/50";
  };

  return (
    <div>
      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <input
          type="text"
          placeholder="Search by name or company..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-sm flex-1 focus:outline-none focus:border-red-500/50 placeholder-white/30"
        />
        <div className="flex gap-2 flex-wrap">
          {INDUSTRIES.map((ind) => (
            <button
              key={ind}
              onClick={() => setIndustryFilter(ind)}
              className={clsx(
                "px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                industryFilter === ind
                  ? "bg-red-700 text-white"
                  : "bg-white/10 text-white/60 hover:bg-white/15"
              )}
            >
              {ind}
            </button>
          ))}
        </div>
      </div>

      {/* Sort */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-white/40 text-sm">
          Showing <span className="text-white">{filtered.length}</span> of {total} billionaires
          {lastUpdated && (
            <span className="ml-2 text-white/25">
              · Updated {new Date(lastUpdated).toLocaleDateString()}
            </span>
          )}
        </p>
        <div className="flex gap-2">
          {(["greed", "net_worth", "giving_ratio"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSortBy(s)}
              className={clsx(
                "px-3 py-1 rounded-lg text-xs transition-colors",
                sortBy === s ? "bg-white/20 text-white" : "text-white/40 hover:text-white/60"
              )}
            >
              {s === "greed" ? "Greed Score" : s === "net_worth" ? "Net Worth" : "Giving Ratio"}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="border border-white/10 rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="grid grid-cols-12 gap-4 px-4 py-3 bg-white/5 border-b border-white/10 text-white/40 text-xs font-medium uppercase tracking-wider">
          <div className="col-span-1">Rank</div>
          <div className="col-span-3">Name</div>
          <div className="col-span-2">Industry</div>
          <div className="col-span-2 text-right">Net Worth</div>
          <div className="col-span-4">Greed Score</div>
        </div>

        {/* Rows */}
        <div className="divide-y divide-white/5">
          {filtered.map((b, i) => {
            const score = b.greed_score ?? 50;
            const tier = getTier(score);
            const color = getScoreColor(score);

            return (
              <motion.div
                key={b.id}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(i * 0.02, 0.5) }}
                className="leaderboard-row"
              >
                <Link href={`/b/${b.slug}`} className="grid grid-cols-12 gap-4 px-4 py-3.5 items-center hover:no-underline">
                  {/* Rank */}
                  <div className="col-span-1">
                    <span className={clsx(
                      "inline-flex items-center justify-center w-8 h-8 rounded-lg border text-xs font-bold font-mono",
                      getRankBadge(b.greed_rank)
                    )}>
                      #{b.greed_rank ?? "—"}
                    </span>
                  </div>

                  {/* Name */}
                  <div className="col-span-3">
                    <div className="font-semibold text-white text-sm">{b.name}</div>
                    <div className="text-white/30 text-xs mt-0.5 truncate">{b.wealth_source}</div>
                    <div className="flex gap-1 mt-1">
                      {b.giving_pledge_signed && (
                        <span className={clsx(
                          "text-xs px-1.5 py-0.5 rounded border",
                          b.giving_pledge_fulfilled
                            ? "bg-green-900/30 text-green-400 border-green-700/30"
                            : "bg-yellow-900/30 text-yellow-400 border-yellow-700/30"
                        )}>
                          {b.giving_pledge_fulfilled ? "✓ Pledge" : "⚠ Pledge"}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Industry */}
                  <div className="col-span-2">
                    <span className="text-white/40 text-xs">{b.industry.split("/")[0].trim()}</span>
                  </div>

                  {/* Net Worth */}
                  <div className="col-span-2 text-right">
                    <div className="font-mono font-bold text-white text-sm">
                      ${b.net_worth_billions.toFixed(1)}B
                    </div>
                    {b.adjusted_giving_billions !== null && (
                      <div className="text-white/30 text-xs">
                        gave ${(b.adjusted_giving_billions).toFixed(2)}B
                      </div>
                    )}
                  </div>

                  {/* Score */}
                  <div className="col-span-4">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono font-black text-base" style={{ color }}>
                        {score.toFixed(1)}
                      </span>
                      <span className={clsx("text-xs font-medium", tier.color)}>
                        {tier.label}
                      </span>
                      {b.loophole_amount_billions !== null && b.loophole_amount_billions > 0 && (
                        <span className="text-xs text-orange-400/70 ml-auto">
                          ⚠ ${b.loophole_amount_billions.toFixed(2)}B loophole
                        </span>
                      )}
                    </div>
                    <GreedMeter score={score} size="sm" showLabel={false} />
                    {b.giving_ratio_pct !== null && (
                      <div className="text-white/25 text-xs mt-1">
                        {b.giving_ratio_pct.toFixed(3)}% of net worth given genuinely
                      </div>
                    )}
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>

      {filtered.length === 0 && (
        <div className="text-center text-white/30 py-12">No results found.</div>
      )}
    </div>
  );
}
