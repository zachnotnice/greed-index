"""
Seed the database with initial billionaire data.
Run with: python -m data.seed
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models.billionaire import Billionaire
from app.models.donation import Donation, Organization
from app.services.scoring import calculate_and_save_scores


def seed():
    init_db()
    db = SessionLocal()

    seed_file = os.path.join(os.path.dirname(__file__), "seed", "billionaires.json")
    with open(seed_file) as f:
        data = json.load(f)

    print(f"Seeding {len(data)} billionaires...")
    org_cache = {}

    for b_data in data:
        # Skip if already exists
        existing = db.query(Billionaire).filter(Billionaire.slug == b_data["slug"]).first()
        if existing:
            print(f"  Skipping {b_data['name']} (already exists)")
            continue

        billionaire = Billionaire(
            slug=b_data["slug"],
            name=b_data["name"],
            net_worth_billions=b_data["net_worth_billions"],
            industry=b_data["industry"],
            wealth_source=b_data["wealth_source"],
            company=b_data.get("company"),
            twitter_handle=b_data.get("twitter_handle"),
            birth_year=b_data.get("birth_year"),
            giving_pledge_signed=b_data.get("giving_pledge_signed", False),
            giving_pledge_fulfilled=b_data.get("giving_pledge_fulfilled", False),
            annual_wealth_growth_pct=b_data.get("annual_wealth_growth_pct", 10.0),
            bio_blurb=b_data.get("bio_blurb", ""),
        )
        db.add(billionaire)
        db.flush()  # get ID

        for d_data in b_data.get("donations", []):
            # Get or create organization
            org_name = d_data.get("organization", {}).get("name") or d_data["organization_name"]
            if org_name not in org_cache:
                org_raw = d_data.get("organization", {})
                org = Organization(
                    name=org_name,
                    cause_category=org_raw.get("cause_category"),
                    overhead_ratio_pct=org_raw.get("overhead_ratio_pct"),
                    payout_ratio_pct=org_raw.get("payout_ratio_pct"),
                    is_transparent=org_raw.get("is_transparent", True),
                )
                db.add(org)
                db.flush()
                org_cache[org_name] = org
            else:
                org = org_cache[org_name]

            donation = Donation(
                billionaire_id=billionaire.id,
                organization_id=org.id,
                organization_name=d_data["organization_name"],
                amount_billions=d_data["amount_billions"],
                year=d_data.get("year"),
                donation_type=d_data.get("donation_type", "direct_grant"),
                verified=True,
            )
            db.add(donation)

        print(f"  Added {b_data['name']}")

    db.commit()

    print("\nCalculating Greed Scores...")
    scores = calculate_and_save_scores(db)
    print(f"Computed {len(scores)} scores.")

    # Print leaderboard
    from app.models.billionaire import GreedScore
    all_scores = db.query(GreedScore).order_by(GreedScore.rank).all()
    print("\n=== GREED INDEX LEADERBOARD ===")
    print(f"{'Rank':<6} {'Name':<25} {'Net Worth':<14} {'Score':<8} {'Giving Ratio'}")
    print("-" * 70)
    for gs in all_scores:
        b = db.query(Billionaire).filter(Billionaire.id == gs.billionaire_id).first()
        print(
            f"#{gs.rank:<5} {b.name:<25} ${b.net_worth_billions:<12.1f}B "
            f"{gs.score:<8.1f} {gs.giving_ratio_pct:.3f}%"
        )

    db.close()
    print("\nDone.")


if __name__ == "__main__":
    seed()
