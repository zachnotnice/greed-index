from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DonationOut(BaseModel):
    id: int
    organization_name: str
    amount_billions: float
    year: Optional[int]
    donation_type: str
    is_loophole: bool
    loophole_reason: Optional[str]
    loophole_pct: float
    verified: bool

    class Config:
        from_attributes = True


class GreedScoreOut(BaseModel):
    score: float
    rank: int
    adjusted_giving_billions: Optional[float]
    total_giving_claimed_billions: Optional[float]
    loophole_amount_billions: Optional[float]
    giving_ratio_pct: Optional[float]
    wealth_penalty: Optional[float]
    quality_score: Optional[float]
    score_breakdown: Optional[Any]
    calculated_at: datetime

    class Config:
        from_attributes = True


class BillionaireListItem(BaseModel):
    id: int
    slug: str
    name: str
    net_worth_billions: float
    industry: str
    wealth_source: str
    photo_url: Optional[str]
    giving_pledge_signed: bool
    giving_pledge_fulfilled: bool
    greed_score: Optional[float]
    greed_rank: Optional[int]
    adjusted_giving_billions: Optional[float]
    giving_ratio_pct: Optional[float]
    loophole_amount_billions: Optional[float]

    class Config:
        from_attributes = True


class BillionaireDetail(BaseModel):
    id: int
    slug: str
    name: str
    net_worth_billions: float
    industry: str
    wealth_source: str
    company: Optional[str]
    twitter_handle: Optional[str]
    wikipedia_url: Optional[str]
    birth_year: Optional[int]
    giving_pledge_signed: bool
    giving_pledge_fulfilled: bool
    bio_blurb: Optional[str]
    annual_wealth_growth_pct: float
    photo_url: Optional[str]
    donations: list[DonationOut]
    latest_score: Optional[GreedScoreOut]
    wealth_per_second: float

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    total: int
    billionaires: list[BillionaireListItem]
    last_updated: Optional[datetime]


class ImpactMetric(BaseModel):
    key: str
    label: str
    count: int
    count_formatted: str
    emoji: str
    category: str


class ImpactResponse(BaseModel):
    amount_billions: float
    metrics: list[ImpactMetric]


class MoveUpResponse(BaseModel):
    current_rank: int
    target_rank: int
    additional_giving_needed_billions: Optional[float]
    already_there: bool
    message: str


class StatsResponse(BaseModel):
    total_billionaires: int
    total_net_worth_billions: float
    total_genuine_giving_billions: float
    total_loophole_giving_billions: float
    average_giving_ratio_pct: float
    giving_pledge_signatories: int
    giving_pledge_fulfilled: int
    most_greedy: Optional[BillionaireListItem]
    least_greedy: Optional[BillionaireListItem]
    industry_breakdown: list[dict]
