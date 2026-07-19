// Greed-tier helpers. Kept in a plain (non-"use client") module so they can be
// called from both server components (e.g. the profile page) and client
// components (GreedMeter, LeaderboardTable). Importing a plain function from a
// "use client" module into a server component turns it into a client-reference
// proxy and throws "getTier is not a function" at runtime.

export const TIERS = [
  { min: 0, max: 20, label: "Generous", color: "text-green-400", bg: "bg-green-500" },
  { min: 20, max: 40, label: "Modest", color: "text-yellow-400", bg: "bg-yellow-500" },
  { min: 40, max: 60, label: "Stingy", color: "text-orange-400", bg: "bg-orange-500" },
  { min: 60, max: 80, label: "Greedy", color: "text-red-400", bg: "bg-red-500" },
  { min: 80, max: 100, label: "Obscenely Greedy", color: "text-red-300", bg: "bg-red-700" },
];

export function getTier(score: number) {
  return TIERS.find((t) => score >= t.min && score <= t.max) || TIERS[TIERS.length - 1];
}

export function getScoreColor(score: number): string {
  if (score < 20) return "#22c55e";
  if (score < 40) return "#eab308";
  if (score < 60) return "#f97316";
  if (score < 80) return "#ef4444";
  return "#b91c1c";
}
