"use client";

import { motion } from "framer-motion";
import clsx from "clsx";
import { getScoreColor, getTier } from "@/lib/tiers";

interface GreedMeterProps {
  score: number; // 0-100
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
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
