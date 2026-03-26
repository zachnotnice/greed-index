"""
Greed Score Engine
------------------
Produces a 0-100 Greed Score for each billionaire. Higher = greedier.

Formula:
  1. Compute adjusted_giving = sum of genuine donation fractions
  2. Giving ratio = adjusted_giving / net_worth
  3. Apply quality multiplier based on cause categories
  4. Compute wealth growth penalty (wealth growing faster than giving)
  5. Normalize across all billionaires to 0-100 scale
  6. Apply Giving Pledge penalty (signed but not followed through)

The score is intentionally transparent so it can be challenged and improved.
"""

import math
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.billionaire import Billionaire, GreedScore
from app.models.donation import Donation, DonationType
from app.services.philanthropy_classifier import classify_donation, get_cause_quality_multiplier


# Weights for score components
GIVING_RATIO_WEIGHT = 0.65
QUALITY_WEIGHT = 0.20
WEALTH_GROWTH_WEIGHT = 0.15

# Giving Pledge signed but not honored: add flat penalty points
UNFULFILLED_PLEDGE_PENALTY = 5.0

# Minimum giving ratio to escape "greediest" tier (0.5% of net worth/year)
MINIMUM_RESPECTABLE_RATIO = 0.005


def compute_adjusted_giving(billionaire: Billionaire) -> dict:
    """
    Sums all donations, applying loophole deductions.
    Returns totals needed for scoring.
    """
    total_claimed = 0.0
    total_genuine = 0.0
    total_loophole = 0.0
    quality_scores = []
    breakdown = []

    for donation in billionaire.donations:
        classification = classify_donation(donation)
        total_claimed += donation.amount_billions
        total_genuine += classification["genuine_amount_billions"]
        total_loophole += classification["loophole_amount_billions"]

        # Quality multiplier from cause
        cause = donation.organization.cause_category if donation.organization else None
        quality_mult = get_cause_quality_multiplier(cause)
        quality_scores.append(quality_mult)

        breakdown.append({
            "organization": donation.organization_name,
            "year": donation.year,
            "claimed_billions": donation.amount_billions,
            "genuine_billions": classification["genuine_amount_billions"],
            "loophole_billions": classification["loophole_amount_billions"],
            "loophole_pct": classification["loophole_pct"],
            "flags": classification["flags"],
            "reason": classification["reason"],
            "donation_type": donation.donation_type,
        })

    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5

    return {
        "total_claimed": total_claimed,
        "total_genuine": total_genuine,
        "total_loophole": total_loophole,
        "avg_quality": avg_quality,
        "breakdown": breakdown,
    }


def compute_wealth_growth_penalty(billionaire: Billionaire) -> float:
    """
    If wealth is growing faster than giving, add a penalty.
    Returns a penalty value 0-10.
    """
    if not billionaire.annual_wealth_growth_pct:
        return 0.0

    wealth_growth = billionaire.annual_wealth_growth_pct

    # Estimate giving growth rate from donations (rough: compare recent vs earlier years)
    donations = sorted(billionaire.donations, key=lambda d: d.year or 0)
    if len(donations) < 2:
        giving_growth = 0.0
    else:
        old = sum(d.amount_billions for d in donations[:len(donations)//2])
        new = sum(d.amount_billions for d in donations[len(donations)//2:])
        if old > 0:
            giving_growth = ((new - old) / old) * 100
        else:
            giving_growth = 0.0

    gap = wealth_growth - giving_growth
    # Every 10 percentage points of gap = 1 penalty point, max 10
    penalty = max(0.0, min(10.0, gap / 10.0))
    return penalty


def raw_greed_score(billionaire: Billionaire) -> dict:
    """
    Computes the raw (pre-normalization) greed score components.
    Lower giving ratio = higher raw greed.
    """
    giving_data = compute_adjusted_giving(billionaire)
    wealth = billionaire.net_worth_billions

    if wealth <= 0:
        return {
            "raw_score": 100.0,
            "giving_ratio_pct": 0.0,
            "giving_component": 100.0,
            "quality_component": 50.0,
            "wealth_penalty": 0.0,
            "pledge_penalty": 0.0,
            "giving_data": {"total_claimed": 0, "total_genuine": 0, "total_loophole": 0, "avg_quality": 0.5, "breakdown": []},
        }

    # Giving ratio: adjusted giving as % of net worth
    giving_ratio = giving_data["total_genuine"] / wealth  # 0.0 to theoretically 1.0+

    # Convert to a "greed component": higher giving ratio = lower greed
    # Use log scale so that going from 0% to 1% matters more than 10% to 11%
    if giving_ratio <= 0:
        giving_component = 100.0
    else:
        # log scale: giving_ratio of 0.01 (1%) -> ~60, 0.10 (10%) -> ~20, 1.0 (100%) -> 0
        giving_component = max(0.0, 100.0 - (math.log10(giving_ratio + 0.001) + 3) * 20)

    # Quality component: low quality giving = higher greed
    quality_component = (1.0 - giving_data["avg_quality"] / 1.2) * 100
    quality_component = max(0.0, min(100.0, quality_component))

    # Wealth growth penalty
    wealth_penalty = compute_wealth_growth_penalty(billionaire)

    # Weighted raw score
    raw = (
        giving_component * GIVING_RATIO_WEIGHT
        + quality_component * QUALITY_WEIGHT
        + wealth_penalty * WEALTH_GROWTH_WEIGHT * 10  # scale penalty to 0-100
    )

    # Giving Pledge penalty
    if billionaire.giving_pledge_signed and not billionaire.giving_pledge_fulfilled:
        raw = min(100.0, raw + UNFULFILLED_PLEDGE_PENALTY)

    return {
        "raw_score": min(100.0, max(0.0, raw)),
        "giving_ratio_pct": giving_ratio * 100,
        "giving_component": giving_component,
        "quality_component": quality_component,
        "wealth_penalty": wealth_penalty,
        "pledge_penalty": UNFULFILLED_PLEDGE_PENALTY if (
            billionaire.giving_pledge_signed and not billionaire.giving_pledge_fulfilled
        ) else 0.0,
        "giving_data": giving_data,
    }


def calculate_and_save_scores(db: Session) -> list[GreedScore]:
    """
    Recalculates scores for all billionaires, normalizes them,
    assigns ranks, and saves to DB.
    """
    billionaires = db.query(Billionaire).all()
    if not billionaires:
        return []

    # Compute raw scores
    raw_results = []
    for b in billionaires:
        result = raw_greed_score(b)
        raw_results.append((b, result))

    # Normalize: map raw scores to 0-100 so the distribution uses the full range
    raw_scores = [r["raw_score"] for _, r in raw_results]
    min_raw = min(raw_scores)
    max_raw = max(raw_scores)
    score_range = max_raw - min_raw if max_raw != min_raw else 1.0

    scored = []
    for b, result in raw_results:
        normalized = ((result["raw_score"] - min_raw) / score_range) * 100
        scored.append((b, result, round(normalized, 1)))

    # Sort by score descending: rank 1 = greediest
    scored.sort(key=lambda x: x[2], reverse=True)

    new_scores = []
    for rank, (b, result, final_score) in enumerate(scored, start=1):
        gd = result["giving_data"]

        # Delete old scores for this billionaire
        db.query(GreedScore).filter(GreedScore.billionaire_id == b.id).delete()

        score_obj = GreedScore(
            billionaire_id=b.id,
            score=final_score,
            rank=rank,
            adjusted_giving_billions=gd["total_genuine"],
            total_giving_claimed_billions=gd["total_claimed"],
            loophole_amount_billions=gd["total_loophole"],
            giving_ratio_pct=result["giving_ratio_pct"],
            wealth_penalty=result["wealth_penalty"],
            quality_score=gd["avg_quality"],
            score_breakdown={
                "giving_component": result["giving_component"],
                "quality_component": result["quality_component"],
                "wealth_penalty": result["wealth_penalty"],
                "pledge_penalty": result["pledge_penalty"],
                "raw_score": result["raw_score"],
                "donation_breakdown": gd["breakdown"],
            },
        )
        db.add(score_obj)
        new_scores.append(score_obj)

    db.commit()
    return new_scores


def what_would_it_take(billionaire: Billionaire, target_rank: int, all_scores: list) -> Optional[float]:
    """
    Calculates how many additional billions the billionaire would need to give
    (in genuine donations) to reach target_rank.
    Returns None if already at or above target rank.
    """
    current_score = billionaire.latest_greed_score
    if not current_score:
        return None

    if current_score.rank <= target_rank:
        return None  # already there

    # Find the score needed to reach target_rank
    if target_rank <= len(all_scores):
        target_score = all_scores[target_rank - 1].score
    else:
        target_score = 0.0

    # Rough inverse: what giving ratio would produce that score?
    # From giving_component formula: score = 100 - (log10(ratio + 0.001) + 3) * 20
    # Solve for ratio given target score component
    target_giving_component = target_score  # simplified approximation
    if target_giving_component >= 100:
        return None

    ratio_needed = 10 ** ((100.0 - target_giving_component) / 20.0 - 3) - 0.001
    needed_giving = max(0.0, ratio_needed * billionaire.net_worth_billions)

    current_genuine = sum(
        classify_donation(d)["genuine_amount_billions"]
        for d in billionaire.donations
    )

    additional = needed_giving - current_genuine
    return max(0.0, additional) if additional > 0 else None
