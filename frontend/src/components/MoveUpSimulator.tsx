"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";

interface MoveUpSimulatorProps {
  slug: string;
  currentRank: number;
  name: string;
  netWorthBillions: number;
}

export default function MoveUpSimulator({ slug, currentRank, name, netWorthBillions }: MoveUpSimulatorProps) {
  const [targetRank, setTargetRank] = useState(Math.max(1, currentRank - 10));
  const [result, setResult] = useState<{
    message: string;
    additional_giving_needed_billions: number | null;
    already_there: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  const simulate = async () => {
    setLoading(true);
    try {
      const data = await api.getMoveUp(slug, targetRank);
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const impactOfNeeded = result?.additional_giving_needed_billions
    ? [
        { emoji: "💉", label: "childhood vaccines", count: Math.round(result.additional_giving_needed_billions * 1e9) },
        { emoji: "🍽️", label: "meals for people in poverty", count: Math.round(result.additional_giving_needed_billions * 5e9) },
        { emoji: "💧", label: "people given clean water access", count: Math.round(result.additional_giving_needed_billions * 4e7) },
      ]
    : [];

  return (
    <div className="bg-black/40 border border-white/10 rounded-2xl p-6 space-y-4">
      <div>
        <h3 className="font-bold text-lg mb-1">Move-Up Simulator</h3>
        <p className="text-white/40 text-sm">
          How much would {name.split(" ")[0]} need to genuinely give to climb the leaderboard?
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex-1">
          <label className="text-white/50 text-xs block mb-1">Target Rank</label>
          <input
            type="number"
            min={1}
            max={currentRank - 1}
            value={targetRank}
            onChange={(e) => setTargetRank(Number(e.target.value))}
            className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm w-full focus:outline-none focus:border-red-500"
          />
        </div>
        <div className="pt-5">
          <span className="text-white/40 text-sm">Currently: #{currentRank}</span>
        </div>
      </div>

      {/* Quick rank buttons */}
      <div className="flex gap-2 flex-wrap">
        {[
          { label: "Top 50%", rank: Math.floor(currentRank * 0.5) },
          { label: "Top 25%", rank: Math.floor(currentRank * 0.25) },
          { label: "Top 10", rank: 10 },
          { label: "Top 5", rank: 5 },
          { label: "#1 Least Greedy", rank: 1 },
        ].filter(p => p.rank < currentRank && p.rank >= 1).map((preset) => (
          <button
            key={preset.label}
            onClick={() => setTargetRank(preset.rank)}
            className={`text-xs px-2.5 py-1 rounded-lg border transition-colors ${
              targetRank === preset.rank
                ? "bg-red-700 border-red-600 text-white"
                : "border-white/20 text-white/50 hover:border-white/40"
            }`}
          >
            {preset.label}
          </button>
        ))}
      </div>

      <button
        onClick={simulate}
        disabled={loading}
        className="w-full bg-red-700 hover:bg-red-600 disabled:opacity-50 text-white font-semibold py-2.5 rounded-xl text-sm transition-colors"
      >
        {loading ? "Calculating..." : `Calculate: Move from #${currentRank} to #${targetRank}`}
      </button>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            {result.already_there ? (
              <div className="bg-green-900/30 border border-green-700/30 rounded-xl p-4 text-green-300 text-sm">
                ✓ {result.message}
              </div>
            ) : (
              <>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-sm">
                  <p className="text-white/70">{result.message}</p>
                  {result.additional_giving_needed_billions && (
                    <p className="text-white/40 text-xs mt-2">
                      That&apos;s{" "}
                      <span className="text-white/70">
                        {((result.additional_giving_needed_billions / netWorthBillions) * 100).toFixed(2)}%
                      </span>{" "}
                      of their net worth.
                    </p>
                  )}
                </div>

                {impactOfNeeded.length > 0 && (
                  <div>
                    <p className="text-white/30 text-xs mb-2">That amount could fund:</p>
                    <div className="grid grid-cols-3 gap-2">
                      {impactOfNeeded.map((item) => (
                        <div key={item.label} className="bg-white/5 rounded-lg p-3 text-center">
                          <div className="text-xl">{item.emoji}</div>
                          <div className="font-mono font-bold text-sm text-white">
                            {item.count.toLocaleString()}
                          </div>
                          <div className="text-white/40 text-xs">{item.label}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
