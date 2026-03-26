"""
Philanthropy Classifier
-----------------------
Determines what fraction of a donation is "genuine" vs a tax loophole.

Loophole criteria (based on IRS research, academic work on philanthropy):
  - Donor-Advised Funds (DAFs): money sits indefinitely, no payout requirement
  - Charitable LLCs: no IRS transparency, donor retains control
  - Conservation Easements: personal property tax dodge
  - Vanity/naming-rights gifts: donor gets commercial value back
  - Private foundations with excessive family salaries or overhead
  - Political 501(c)(4)s disguised as social welfare orgs
  - Giving Pledge signatures with no actual transfers
  - Impact investments where donor retains equity/control
"""

from app.models.donation import DonationType


LOOPHOLE_RULES = {
    DonationType.DAF: {
        "loophole_pct": 0.5,  # 50% — money may sit forever, but some does eventually get paid out
        "reason": "Donor-Advised Funds have no mandatory payout timeline. Funds can sit indefinitely "
                  "while the donor has already taken the tax deduction. Half credit given for eventual distribution.",
    },
    DonationType.CHARITABLE_LLC: {
        "loophole_pct": 1.0,
        "reason": "Charitable LLCs (e.g., Chan Zuckerberg Initiative) are not subject to IRS transparency "
                  "requirements, have no mandatory payout, and allow the donor to retain full control of assets. "
                  "These are investment vehicles, not charities.",
    },
    DonationType.CONSERVATION_EASEMENT: {
        "loophole_pct": 1.0,
        "reason": "Conservation easements on personal property are a well-documented IRS abuse. "
                  "The donor retains use of the land while claiming a massive deduction based on "
                  "inflated appraisals. No genuine social benefit.",
    },
    DonationType.NAMING_RIGHTS: {
        "loophole_pct": 0.4,
        "reason": "Naming rights donations provide commercial value back to the donor (brand building, "
                  "prestige, advertising). The portion attributable to personal benefit is excluded. "
                  "40% classified as loophole for vanity premium.",
    },
    DonationType.POLITICAL: {
        "loophole_pct": 0.8,
        "reason": "Political 'charity' through 501(c)(4)s, PACs, or ideological advocacy organizations "
                  "that advance the donor's business interests or political agenda are not genuine philanthropy. "
                  "80% excluded — some legitimate social welfare value may exist.",
    },
    DonationType.GIVING_PLEDGE: {
        "loophole_pct": 1.0,
        "reason": "The Giving Pledge is a voluntary, legally non-binding commitment with no enforcement mechanism. "
                  "Signing costs nothing. No credit until actual transfers occur.",
    },
    DonationType.IMPACT_INVESTMENT: {
        "loophole_pct": 0.7,
        "reason": "Impact investments where the donor retains equity and control are not donations — "
                  "they are investments with social marketing. 70% excluded; 30% credit for genuine "
                  "below-market-rate social value created.",
    },
    DonationType.FOUNDATION: {
        "loophole_pct": 0.0,  # base rate — adjusted by overhead check below
        "reason": None,
    },
    DonationType.DIRECT_GRANT: {
        "loophole_pct": 0.0,
        "reason": None,
    },
    DonationType.IN_KIND: {
        "loophole_pct": 0.1,
        "reason": "In-kind donations sometimes involve overvalued assets. Small loophole penalty applied.",
    },
}

# If a private foundation has high overhead, penalize proportionally
FOUNDATION_OVERHEAD_THRESHOLD = 0.20  # 20% — above this is considered excessive
FOUNDATION_FAMILY_SALARY_PENALTY = 0.5  # if family members are highly compensated


def classify_donation(donation) -> dict:
    """
    Returns a dict with:
      - loophole_pct: fraction of donation that's a loophole (0.0 = all genuine, 1.0 = all loophole)
      - genuine_amount: dollars that count toward genuine giving
      - reason: explanation
      - flags: list of specific issues found
    """
    dtype = donation.donation_type
    rule = LOOPHOLE_RULES.get(dtype, {"loophole_pct": 0.0, "reason": None})

    loophole_pct = rule["loophole_pct"]
    reasons = []
    flags = []

    if rule["reason"]:
        reasons.append(rule["reason"])
        flags.append(dtype)

    # Extra check for foundations: overhead ratio
    if dtype == DonationType.FOUNDATION and donation.organization:
        org = donation.organization
        if org.overhead_ratio_pct and org.overhead_ratio_pct > FOUNDATION_OVERHEAD_THRESHOLD * 100:
            excess = (org.overhead_ratio_pct / 100 - FOUNDATION_OVERHEAD_THRESHOLD)
            overhead_penalty = min(0.5, excess * 2)  # scale: 20%->0, 45%->0.5
            loophole_pct = max(loophole_pct, overhead_penalty)
            reasons.append(
                f"Foundation overhead is {org.overhead_ratio_pct:.0f}% — above the 20% threshold. "
                f"Portion attributed to administrative bloat is excluded."
            )
            flags.append("high_overhead")

        if org.payout_ratio_pct and org.payout_ratio_pct < 5.0:
            # IRS requires 5% minimum payout for private foundations
            low_payout_penalty = 0.3
            loophole_pct = max(loophole_pct, low_payout_penalty)
            reasons.append(
                f"Foundation payout ratio is {org.payout_ratio_pct:.1f}% — near the IRS 5% minimum. "
                f"Low distribution reduces genuine social impact."
            )
            flags.append("low_payout")

    genuine_pct = 1.0 - loophole_pct
    genuine_amount = donation.amount_billions * genuine_pct
    loophole_amount = donation.amount_billions * loophole_pct

    return {
        "loophole_pct": loophole_pct,
        "genuine_pct": genuine_pct,
        "genuine_amount_billions": genuine_amount,
        "loophole_amount_billions": loophole_amount,
        "reason": " | ".join(reasons) if reasons else "Genuine donation — no loophole flags.",
        "flags": flags,
    }


def get_cause_quality_multiplier(cause_category: str) -> float:
    """
    Multiplier based on the social impact priority of the cause.
    Funds going to highest-need causes get a slight quality bonus.
    """
    HIGH_IMPACT = {"global_health", "poverty", "hunger", "pandemic_prevention", "climate"}
    MEDIUM_IMPACT = {"education", "housing", "criminal_justice", "mental_health", "veterans"}
    LOW_IMPACT = {"arts", "universities", "hospitals", "religious"}  # often wealthy-serving

    cat = (cause_category or "").lower()
    if any(h in cat for h in HIGH_IMPACT):
        return 1.2
    elif any(m in cat for m in MEDIUM_IMPACT):
        return 1.0
    elif any(l in cat for l in LOW_IMPACT):
        return 0.8
    return 1.0
