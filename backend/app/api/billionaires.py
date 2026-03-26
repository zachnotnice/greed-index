from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.billionaire import Billionaire, GreedScore
from app.models.donation import Donation
from app.schemas.billionaire import (
    BillionaireDetail, BillionaireListItem, LeaderboardResponse,
    ImpactResponse, MoveUpResponse, StatsResponse
)
from app.services.impact_calculator import calculate_impact, wealth_per_second
from app.services.scoring import calculate_and_save_scores, what_would_it_take
from app.services.philanthropy_classifier import classify_donation

router = APIRouter(prefix="/api", tags=["billionaires"])


def _enrich_billionaire(b: Billionaire, score: Optional[GreedScore]) -> dict:
    return {
        "id": b.id,
        "slug": b.slug,
        "name": b.name,
        "net_worth_billions": b.net_worth_billions,
        "industry": b.industry,
        "wealth_source": b.wealth_source,
        "company": b.company,
        "twitter_handle": b.twitter_handle,
        "wikipedia_url": b.wikipedia_url,
        "birth_year": b.birth_year,
        "giving_pledge_signed": b.giving_pledge_signed,
        "giving_pledge_fulfilled": b.giving_pledge_fulfilled,
        "bio_blurb": b.bio_blurb,
        "annual_wealth_growth_pct": b.annual_wealth_growth_pct,
        "photo_url": b.photo_url,
        "greed_score": score.score if score else None,
        "greed_rank": score.rank if score else None,
        "adjusted_giving_billions": score.adjusted_giving_billions if score else None,
        "giving_ratio_pct": score.giving_ratio_pct if score else None,
        "loophole_amount_billions": score.loophole_amount_billions if score else None,
    }


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    db: Session = Depends(get_db),
    industry: Optional[str] = Query(None),
    sort_by: str = Query("greed", enum=["greed", "net_worth", "giving_ratio"]),
    limit: int = Query(200, le=200),
    offset: int = Query(0),
):
    query = db.query(Billionaire)
    if industry:
        query = query.filter(Billionaire.industry.ilike(f"%{industry}%"))

    billionaires = query.all()

    # Get latest scores
    results = []
    for b in billionaires:
        scores = sorted(b.greed_scores, key=lambda s: s.calculated_at, reverse=True)
        score = scores[0] if scores else None
        results.append((b, score))

    # Sort
    if sort_by == "greed":
        results.sort(key=lambda x: x[1].rank if x[1] else 9999)
    elif sort_by == "net_worth":
        results.sort(key=lambda x: x[0].net_worth_billions, reverse=True)
    elif sort_by == "giving_ratio":
        results.sort(key=lambda x: x[1].giving_ratio_pct if x[1] else 0)

    total = len(results)
    results = results[offset:offset + limit]

    last_score = db.query(GreedScore).order_by(GreedScore.calculated_at.desc()).first()

    return {
        "total": total,
        "billionaires": [_enrich_billionaire(b, s) for b, s in results],
        "last_updated": last_score.calculated_at if last_score else None,
    }


@router.get("/billionaires/{slug}", response_model=BillionaireDetail)
def get_billionaire(slug: str, db: Session = Depends(get_db)):
    b = db.query(Billionaire).filter(Billionaire.slug == slug).first()
    if not b:
        raise HTTPException(status_code=404, detail="Billionaire not found")

    scores = sorted(b.greed_scores, key=lambda s: s.calculated_at, reverse=True)
    latest_score = scores[0] if scores else None

    # Enrich donations with loophole classification
    enriched_donations = []
    for d in b.donations:
        classification = classify_donation(d)
        enriched_donations.append({
            "id": d.id,
            "organization_name": d.organization_name,
            "amount_billions": d.amount_billions,
            "year": d.year,
            "donation_type": d.donation_type,
            "is_loophole": classification["loophole_pct"] > 0,
            "loophole_reason": classification["reason"],
            "loophole_pct": classification["loophole_pct"],
            "verified": d.verified,
        })

    return {
        **_enrich_billionaire(b, latest_score),
        "donations": enriched_donations,
        "latest_score": latest_score,
        "wealth_per_second": wealth_per_second(b.net_worth_billions, b.annual_wealth_growth_pct),
    }


@router.get("/impact")
def get_impact(amount_billions: float = Query(..., gt=0), db: Session = Depends(get_db)):
    metrics = calculate_impact(amount_billions)
    return {"amount_billions": amount_billions, "metrics": metrics}


@router.get("/billionaires/{slug}/move-up")
def get_move_up(slug: str, target_rank: int = Query(..., ge=1), db: Session = Depends(get_db)):
    b = db.query(Billionaire).filter(Billionaire.slug == slug).first()
    if not b:
        raise HTTPException(status_code=404, detail="Billionaire not found")

    scores = sorted(b.greed_scores, key=lambda s: s.calculated_at, reverse=True)
    current_score = scores[0] if scores else None

    if not current_score:
        return {"error": "No score computed yet"}

    if current_score.rank <= target_rank:
        return MoveUpResponse(
            current_rank=current_score.rank,
            target_rank=target_rank,
            additional_giving_needed_billions=None,
            already_there=True,
            message=f"{b.name} is already at rank #{current_score.rank}, better than #{target_rank}.",
        )

    all_scores = db.query(GreedScore).order_by(GreedScore.rank).all()
    additional = what_would_it_take(b, target_rank, all_scores)

    if additional is None:
        msg = f"{b.name} cannot reach rank #{target_rank} with current data."
    else:
        msg = (
            f"If {b.name} donated an additional ${additional:.2f}B in genuine giving, "
            f"they could move from rank #{current_score.rank} to #{target_rank}."
        )

    return MoveUpResponse(
        current_rank=current_score.rank,
        target_rank=target_rank,
        additional_giving_needed_billions=additional,
        already_there=False,
        message=msg,
    )


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    billionaires = db.query(Billionaire).all()
    all_scores = db.query(GreedScore).order_by(GreedScore.rank).all()

    total_nw = sum(b.net_worth_billions for b in billionaires)
    total_genuine = sum(s.adjusted_giving_billions or 0 for s in all_scores)
    total_loophole = sum(s.loophole_amount_billions or 0 for s in all_scores)
    avg_ratio = sum(s.giving_ratio_pct or 0 for s in all_scores) / len(all_scores) if all_scores else 0

    pledge_signatories = sum(1 for b in billionaires if b.giving_pledge_signed)
    pledge_fulfilled = sum(1 for b in billionaires if b.giving_pledge_fulfilled)

    # Industry breakdown
    industry_map = {}
    for b in billionaires:
        ind = b.industry.split("/")[0].strip()
        scores = sorted(b.greed_scores, key=lambda s: s.calculated_at, reverse=True)
        score = scores[0].score if scores else 50
        if ind not in industry_map:
            industry_map[ind] = {"industry": ind, "count": 0, "avg_score": 0, "scores": []}
        industry_map[ind]["count"] += 1
        industry_map[ind]["scores"].append(score)

    industry_breakdown = []
    for ind, data in industry_map.items():
        industry_breakdown.append({
            "industry": data["industry"],
            "count": data["count"],
            "avg_greed_score": sum(data["scores"]) / len(data["scores"]),
        })
    industry_breakdown.sort(key=lambda x: x["avg_greed_score"], reverse=True)

    # Most/least greedy
    def billionaire_summary(b: Billionaire, s: Optional[GreedScore]):
        return _enrich_billionaire(b, s) if b else None

    most_greedy_score = all_scores[0] if all_scores else None
    least_greedy_score = all_scores[-1] if all_scores else None

    most_greedy_b = db.query(Billionaire).filter(
        Billionaire.id == most_greedy_score.billionaire_id
    ).first() if most_greedy_score else None

    least_greedy_b = db.query(Billionaire).filter(
        Billionaire.id == least_greedy_score.billionaire_id
    ).first() if least_greedy_score else None

    return {
        "total_billionaires": len(billionaires),
        "total_net_worth_billions": total_nw,
        "total_genuine_giving_billions": total_genuine,
        "total_loophole_giving_billions": total_loophole,
        "average_giving_ratio_pct": avg_ratio,
        "giving_pledge_signatories": pledge_signatories,
        "giving_pledge_fulfilled": pledge_fulfilled,
        "most_greedy": billionaire_summary(most_greedy_b, most_greedy_score),
        "least_greedy": billionaire_summary(least_greedy_b, least_greedy_score),
        "industry_breakdown": industry_breakdown,
    }


@router.post("/recalculate")
def recalculate_scores(db: Session = Depends(get_db)):
    scores = calculate_and_save_scores(db)
    return {"message": f"Recalculated {len(scores)} scores successfully."}
