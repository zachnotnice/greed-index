"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface WealthClockProps {
  wealthPerSecond: number;
  name: string;
  compact?: boolean;
}

export default function WealthClock({ wealthPerSecond, name, compact = false }: WealthClockProps) {
  const [accumulated, setAccumulated] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      setAccumulated(elapsed * wealthPerSecond);
    }, 100);
    return () => clearInterval(interval);
  }, [wealthPerSecond, startTime]);

  const formatMoney = (dollars: number): string => {
    if (dollars >= 1_000_000) return `$${(dollars / 1_000_000).toFixed(2)}M`;
    if (dollars >= 1_000) return `$${(dollars / 1_000).toFixed(2)}K`;
    return `$${dollars.toFixed(2)}`;
  };

  if (compact) {
    return (
      <div className="flex items-center gap-2 text-sm">
        <span className="text-white/40">Earned since you opened this page:</span>
        <span className="font-mono font-bold text-green-400 tabular-nums">
          {formatMoney(accumulated)}
        </span>
      </div>
    );
  }

  return (
    <div className="bg-black/40 border border-white/10 rounded-xl p-6 text-center">
      <p className="text-white/50 text-sm mb-2">
        Since you opened this page, {name.split(" ")[0]} has accumulated approximately:
      </p>
      <div className="text-4xl font-mono font-bold text-green-400 tabular-nums mb-1">
        {formatMoney(accumulated)}
      </div>
      <p className="text-white/30 text-xs">
        ≈ ${(wealthPerSecond).toFixed(2)}/second · ${(wealthPerSecond * 3600).toLocaleString()}/hour
      </p>
      <div className="mt-4 grid grid-cols-3 gap-3 text-sm">
        <div className="bg-white/5 rounded-lg p-3">
          <div className="font-mono font-bold text-yellow-400">
            ${(wealthPerSecond * 60).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
          <div className="text-white/40 text-xs">per minute</div>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="font-mono font-bold text-orange-400">
            ${(wealthPerSecond * 3600).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
          <div className="text-white/40 text-xs">per hour</div>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="font-mono font-bold text-red-400">
            ${(wealthPerSecond * 86400 / 1000).toFixed(1)}K
          </div>
          <div className="text-white/40 text-xs">per day</div>
        </div>
      </div>
    </div>
  );
}
