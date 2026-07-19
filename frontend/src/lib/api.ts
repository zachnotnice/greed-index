// Static data layer.
//
// The site ships with a precomputed dataset (src/data/greed-data.json, produced
// by `python -m data.export_static` in the backend) instead of calling a live
// API. These functions read from that JSON, so there is no backend server to
// run or host. To update the data: edit the seed, re-run the export script, and
// commit the regenerated greed-data.json.
//
// NOTE: this module statically imports the ~700 KB dataset, so it must only be
// imported by SERVER components (the home and profile pages). Client components
// use pure helpers in ./calc instead. Types below are safe to import anywhere
// via `import type`.

import greedData from "@/data/greed-data.json";

export interface BillionaireListItem {
  id: number;
  slug: string;
  name: string;
  net_worth_billions: number;
  industry: string;
  wealth_source: string;
  photo_url: string | null;
  giving_pledge_signed: boolean;
  giving_pledge_fulfilled: boolean;
  greed_score: number | null;
  greed_rank: number | null;
  adjusted_giving_billions: number | null;
  giving_ratio_pct: number | null;
  loophole_amount_billions: number | null;
}

export interface Donation {
  id: number;
  organization_name: string;
  amount_billions: number;
  year: number | null;
  donation_type: string;
  is_loophole: boolean;
  loophole_reason: string | null;
  loophole_pct: number;
  verified: boolean;
}

export interface GreedScore {
  score: number;
  rank: number;
  adjusted_giving_billions: number | null;
  total_giving_claimed_billions: number | null;
  loophole_amount_billions: number | null;
  giving_ratio_pct: number | null;
  wealth_penalty: number | null;
  quality_score: number | null;
  score_breakdown: Record<string, unknown> | null;
  calculated_at: string;
}

export interface BillionaireDetail extends BillionaireListItem {
  company: string | null;
  twitter_handle: string | null;
  wikipedia_url: string | null;
  birth_year: number | null;
  bio_blurb: string | null;
  annual_wealth_growth_pct: number;
  donations: Donation[];
  latest_score: GreedScore | null;
  wealth_per_second: number;
}

export interface LeaderboardResponse {
  total: number;
  billionaires: BillionaireListItem[];
  last_updated: string | null;
}

export interface ImpactMetric {
  key: string;
  label: string;
  count: number;
  count_formatted: string;
  emoji: string;
  category: string;
}

export interface Stats {
  total_billionaires: number;
  total_net_worth_billions: number;
  total_genuine_giving_billions: number;
  total_loophole_giving_billions: number;
  average_giving_ratio_pct: number;
  giving_pledge_signatories: number;
  giving_pledge_fulfilled: number;
  most_greedy: BillionaireListItem | null;
  least_greedy: BillionaireListItem | null;
  industry_breakdown: Array<{ industry: string; count: number; avg_greed_score: number }>;
}

interface GreedData {
  generated_at: string;
  leaderboard: LeaderboardResponse;
  stats: Stats;
  billionaires: Record<string, BillionaireDetail>;
}

const data = greedData as unknown as GreedData;

export const api = {
  getLeaderboard: async (params?: {
    industry?: string;
    sort_by?: "greed" | "net_worth" | "giving_ratio";
    limit?: number;
  }): Promise<LeaderboardResponse> => {
    let list = [...data.leaderboard.billionaires];

    if (params?.industry) {
      const needle = params.industry.toLowerCase();
      list = list.filter((b) => b.industry.toLowerCase().includes(needle));
    }

    const sortBy = params?.sort_by ?? "greed";
    if (sortBy === "greed") {
      list.sort((a, b) => (a.greed_rank ?? 9999) - (b.greed_rank ?? 9999));
    } else if (sortBy === "net_worth") {
      list.sort((a, b) => b.net_worth_billions - a.net_worth_billions);
    } else if (sortBy === "giving_ratio") {
      list.sort((a, b) => (a.giving_ratio_pct ?? 0) - (b.giving_ratio_pct ?? 0));
    }

    const total = list.length;
    if (params?.limit != null) list = list.slice(0, params.limit);

    return { total, billionaires: list, last_updated: data.leaderboard.last_updated };
  },

  getBillionaire: async (slug: string): Promise<BillionaireDetail> => {
    const b = data.billionaires[slug];
    if (!b) throw new Error(`Billionaire not found: ${slug}`);
    return b;
  },

  getStats: async (): Promise<Stats> => data.stats,
};
