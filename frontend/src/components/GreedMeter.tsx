"use client";

import { motion } from "framer-motion";
import clsx from "clsx";

interface GreedMeterProps {
  score: number; // 0-100
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

const TIERS = [
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

export default function GreedMeter({ score, size = "md", showLabel = true }: GreedMeterProps) {
  const tier = getTier(score);
  const color = getScoreColor(score);

  const sizeClasses = {
    sm: "h-1.5 text-xs",
    md: "h-2 text-sm",
    lg: "h-3 text-base",
  };

  return (
    <div className="w-full">
      <div className={clsx("relative w-full bg-white/10 rounded-full overflow-hidden", sizeClasses[size].split(" ")[0])}>
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between items-center mt-1">
          <span className={clsx("font-semibold", sizeClasses[size].split(" ")[1], tier.color)}>
            {tier.label}
          </span>
          <span className={clsx("font-mono font-bold", sizeClasses[size].split(" ")[1])} style={{ color }}>
            {score.toFixed(1)}
          </span>
        </div>
      )}
    </div>
  );
}
