"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, ImpactMetric } from "@/lib/api";

interface ImpactCalculatorProps {
  defaultAmount?: number;
  label?: string;
}

export default function ImpactCalculator({
  defaultAmount = 1,
  label = "Enter an amount in billions",
}: ImpactCalculatorProps) {
  const [amount, setAmount] = useState(defaultAmount);
  const [metrics, setMetrics] = useState<ImpactMetric[]>([]);
  const [loading, setLoading] = useState(false);

  const calculate = useCallback(async (val: number) => {
    if (val <= 0) return;
    setLoading(true);
    try {
      const result = await api.getImpact(val);
      setMetrics(result.metrics);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const PRESETS = [
    { label: "$100M", value: 0.1 },
    { label: "$1B", value: 1 },
    { label: "$10B", value: 10 },
    { label: "$50B", value: 50 },
    { label: "$100B", value: 100 },
  ];

  const FEATURED_METRICS = ["lives_saved_malaria", "clean_water", "meals", "school_years", "solar_homes"];
  const featured = metrics.filter((m) => FEATURED_METRICS.includes(m.key));

  return (
    <div className="space-y-4">
      <div>
        <label className="text-white/50 text-sm block mb-2">{label}</label>
        <div className="flex gap-2 flex-wrap">
          {PRESETS.map((p) => (
            <button
              key={p.value}
              onClick={() => { setAmount(p.value); calculate(p.value); }}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                amount === p.value
                  ? "bg-red-600 text-white"
                  : "bg-white/10 text-white/70 hover:bg-white/20"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
        <div className="flex gap-2 mt-2">
          <input
            type="number"
            value={amount}
            min={0.001}
            step={0.1}
            onChange={(e) => setAmount(Number(e.target.value))}
            className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm w-32 focus:outline-none focus:border-red-500"
            placeholder="Billions"
          />
          <button
            onClick={() => calculate(amount)}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Calculate Impact
          </button>
        </div>
      </div>

      <AnimatePresence>
        {loading && (
          <div className="text-white/40 text-sm animate-pulse">Calculating...</div>
        )}
        {!loading && featured.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-2 sm:grid-cols-3 gap-3"
          >
            {featured.map((m) => (
              <div key={m.key} className="bg-white/5 border border-white/10 rounded-xl p-4">
                <div className="text-2xl mb-1">{m.emoji}</div>
                <div className="font-mono font-bold text-lg text-white">{m.count_formatted}</div>
                <div className="text-white/50 text-xs mt-1">{m.label}</div>
              </div>
            ))}
          </motion.div>
        )}
        {!loading && metrics.length > 0 && (
          <details className="text-sm">
            <summary className="text-white/40 cursor-pointer hover:text-white/60 transition-colors">
              Show all {metrics.length} impact metrics
            </summary>
            <div className="mt-2 grid grid-cols-2 sm:grid-cols-4 gap-2">
              {metrics.filter((m) => !FEATURED_METRICS.includes(m.key)).map((m) => (
                <div key={m.key} className="bg-white/5 rounded-lg p-3 text-sm">
                  <span className="mr-1">{m.emoji}</span>
                  <span className="font-mono font-bold">{m.count_formatted}</span>
                  <div className="text-white/40 text-xs mt-0.5">{m.label}</div>
                </div>
              ))}
            </div>
          </details>
        )}
      </AnimatePresence>
    </div>
  );
}
