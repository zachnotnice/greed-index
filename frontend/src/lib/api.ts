const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

async function fetchAPI<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getLeaderboard: (params?: { industry?: string; sort_by?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.industry) qs.set("industry", params.industry);
    if (params?.sort_by) qs.set("sort_by", params.sort_by);
    if (params?.limit) qs.set("limit", String(params.limit));
    return fetchAPI<LeaderboardResponse>(`/api/leaderboard?${qs}`);
  },

  getBillionaire: (slug: string) =>
    fetchAPI<BillionaireDetail>(`/api/billionaires/${slug}`),

  getImpact: (amountBillions: number) =>
    fetchAPI<{ amount_billions: number; metrics: ImpactMetric[] }>(
      `/api/impact?amount_billions=${amountBillions}`
    ),

  getMoveUp: (slug: string, targetRank: number) =>
    fetchAPI<{
      current_rank: number;
      target_rank: number;
      additional_giving_needed_billions: number | null;
      already_there: boolean;
      message: string;
    }>(`/api/billionaires/${slug}/move-up?target_rank=${targetRank}`),

  getStats: () => fetchAPI<Stats>("/api/stats"),
};
