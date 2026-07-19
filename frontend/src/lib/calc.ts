// Pure, client-safe calculators. These were formerly the backend's
// /api/impact and /api/billionaires/{slug}/move-up endpoints; ported to
// TypeScript so the interactive widgets work with no server.
//
// Kept free of any data-file import so it stays tiny in the client bundle.

import type { ImpactMetric } from "@/lib/api";

// Cost-per-unit is dollars-of-impact per dollar spent (i.e. 1 / unit_cost),
// matching backend/app/services/impact_calculator.py.
const IMPACT_METRICS = [
  { key: "malaria_nets", label: "malaria-preventing bed nets distributed", cost_per_unit: 0.0000025, emoji: "🦟", category: "global_health" },
  { key: "lives_saved_malaria", label: "lives saved from malaria (GiveWell estimate)", cost_per_unit: 0.005, emoji: "❤️", category: "global_health" },
  { key: "vaccines", label: "childhood vaccines delivered", cost_per_unit: 0.000001, emoji: "💉", category: "global_health" },
  { key: "school_years", label: "years of quality education funded", cost_per_unit: 0.0000012, emoji: "📚", category: "education" },
  { key: "teachers_hired", label: "US public school teachers hired for a year", cost_per_unit: 0.000068, emoji: "👩‍🏫", category: "education" },
  { key: "clean_water", label: "people given access to clean water for life", cost_per_unit: 0.000025, emoji: "💧", category: "poverty" },
  { key: "meals", label: "meals provided to people in poverty", cost_per_unit: 0.0000002, emoji: "🍽️", category: "hunger" },
  { key: "homes_built", label: "affordable homes built (Habitat for Humanity estimate)", cost_per_unit: 0.00015, emoji: "🏠", category: "housing" },
  { key: "solar_homes", label: "homes powered by solar energy", cost_per_unit: 0.000025, emoji: "☀️", category: "climate" },
  { key: "carbon_offset_tons", label: "tons of CO₂ offset", cost_per_unit: 0.00001, emoji: "🌍", category: "climate" },
  { key: "ev_charging_stations", label: "EV charging stations installed", cost_per_unit: 0.00005, emoji: "⚡", category: "climate" },
  { key: "mental_health_sessions", label: "mental health therapy sessions funded", cost_per_unit: 0.000175, emoji: "🧠", category: "mental_health" },
  { key: "icu_beds", label: "ICU bed-days funded at US hospitals", cost_per_unit: 0.004, emoji: "🏥", category: "healthcare" },
  { key: "small_business_loans", label: "small business microloans in developing nations", cost_per_unit: 0.000001, emoji: "💼", category: "poverty" },
];

function formatLargeNumber(n: number): string {
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export function calculateImpact(amountBillions: number): ImpactMetric[] {
  const amountDollars = amountBillions * 1_000_000_000;
  const results: ImpactMetric[] = [];
  for (const m of IMPACT_METRICS) {
    const count = Math.floor(amountDollars * m.cost_per_unit);
    if (count >= 1) {
      results.push({
        key: m.key,
        label: m.label,
        count,
        count_formatted: formatLargeNumber(count),
        emoji: m.emoji,
        category: m.category,
      });
    }
  }
  return results;
}

export interface MoveUpResult {
  current_rank: number;
  target_rank: number;
  additional_giving_needed_billions: number | null;
  already_there: boolean;
  message: string;
}

/**
 * How much additional genuine giving would move a billionaire to targetRank.
 * Ported from backend scoring.what_would_it_take + the move-up endpoint.
 *
 * @param scoresByRank scores ordered by rank ascending (index 0 = rank #1).
 */
export function whatWouldItTake(params: {
  name: string;
  currentRank: number;
  targetRank: number;
  netWorthBillions: number;
  currentGenuineBillions: number;
  scoresByRank: number[];
}): MoveUpResult {
  const { name, currentRank, targetRank, netWorthBillions, currentGenuineBillions, scoresByRank } = params;

  if (currentRank <= targetRank) {
    return {
      current_rank: currentRank,
      target_rank: targetRank,
      additional_giving_needed_billions: null,
      already_there: true,
      message: `${name} is already at rank #${currentRank}, better than #${targetRank}.`,
    };
  }

  const targetScore = targetRank <= scoresByRank.length ? scoresByRank[targetRank - 1] : 0;
  let additional: number | null = null;
  if (targetScore < 100) {
    const ratioNeeded = Math.pow(10, (100 - targetScore) / 20 - 3) - 0.001;
    const neededGiving = Math.max(0, ratioNeeded * netWorthBillions);
    const a = neededGiving - currentGenuineBillions;
    additional = a > 0 ? a : null;
  }

  const message =
    additional === null
      ? `${name} cannot reach rank #${targetRank} with current data.`
      : `If ${name} donated an additional $${additional.toFixed(2)}B in genuine giving, ` +
        `they could move from rank #${currentRank} to #${targetRank}.`;

  return {
    current_rank: currentRank,
    target_rank: targetRank,
    additional_giving_needed_billions: additional,
    already_there: false,
    message,
  };
}
