"""
Impact Calculator
-----------------
Converts billions of dollars into tangible real-world outcomes.
Used in the "What Could This Do?" feature.

Sources: UN, WHO, GiveWell, World Bank cost-effectiveness estimates.
"""

IMPACT_METRICS = [
    {
        "key": "malaria_nets",
        "label": "malaria-preventing bed nets distributed",
        "cost_per_unit": 0.0000025,  # $2.50 each
        "emoji": "🦟",
        "category": "global_health",
    },
    {
        "key": "lives_saved_malaria",
        "label": "lives saved from malaria (GiveWell estimate)",
        "cost_per_unit": 0.005,  # ~$5,000 per life saved via Against Malaria Foundation
        "emoji": "❤️",
        "category": "global_health",
    },
    {
        "key": "vaccines",
        "label": "childhood vaccines delivered",
        "cost_per_unit": 0.000001,  # ~$1 each via GAVI
        "emoji": "💉",
        "category": "global_health",
    },
    {
        "key": "school_years",
        "label": "years of quality education funded",
        "cost_per_unit": 0.0000012,  # ~$1,200/year per child in developing nations
        "emoji": "📚",
        "category": "education",
    },
    {
        "key": "teachers_hired",
        "label": "US public school teachers hired for a year",
        "cost_per_unit": 0.000068,  # ~$68,000 average teacher salary + benefits
        "emoji": "👩‍🏫",
        "category": "education",
    },
    {
        "key": "clean_water",
        "label": "people given access to clean water for life",
        "cost_per_unit": 0.000025,  # ~$25 per person via Water.org
        "emoji": "💧",
        "category": "poverty",
    },
    {
        "key": "meals",
        "label": "meals provided to people in poverty",
        "cost_per_unit": 0.0000002,  # ~$0.20 per meal via food banks
        "emoji": "🍽️",
        "category": "hunger",
    },
    {
        "key": "homes_built",
        "label": "affordable homes built (Habitat for Humanity estimate)",
        "cost_per_unit": 0.00015,  # ~$150,000 per home
        "emoji": "🏠",
        "category": "housing",
    },
    {
        "key": "solar_homes",
        "label": "homes powered by solar energy",
        "cost_per_unit": 0.000025,  # ~$25,000 per home system
        "emoji": "☀️",
        "category": "climate",
    },
    {
        "key": "carbon_offset_tons",
        "label": "tons of CO₂ offset",
        "cost_per_unit": 0.00001,  # ~$10 per ton via high-quality offsets
        "emoji": "🌍",
        "category": "climate",
    },
    {
        "key": "ev_charging_stations",
        "label": "EV charging stations installed",
        "cost_per_unit": 0.00005,  # ~$50,000 per DC fast charger
        "emoji": "⚡",
        "category": "climate",
    },
    {
        "key": "mental_health_sessions",
        "label": "mental health therapy sessions funded",
        "cost_per_unit": 0.000175,  # ~$175 per session
        "emoji": "🧠",
        "category": "mental_health",
    },
    {
        "key": "icu_beds",
        "label": "ICU bed-days funded at US hospitals",
        "cost_per_unit": 0.004,  # ~$4,000/day
        "emoji": "🏥",
        "category": "healthcare",
    },
    {
        "key": "small_business_loans",
        "label": "small business microloans in developing nations",
        "cost_per_unit": 0.000001,  # ~$1,000 each via Kiva-style programs
        "emoji": "💼",
        "category": "poverty",
    },
]


def calculate_impact(amount_billions: float) -> list[dict]:
    """
    Given an amount in billions, returns a list of impact metrics
    showing what that money could accomplish.
    """
    amount_dollars = amount_billions * 1_000_000_000
    results = []

    for metric in IMPACT_METRICS:
        count = amount_dollars * metric["cost_per_unit"]
        if count >= 1:
            results.append({
                "key": metric["key"],
                "label": metric["label"],
                "count": int(count),
                "count_formatted": _format_large_number(int(count)),
                "emoji": metric["emoji"],
                "category": metric["category"],
            })

    return results


def wealth_per_second(net_worth_billions: float, growth_rate_pct: float = 15.0) -> float:
    """
    Approximate wealth accumulation per second based on net worth and growth rate.
    Default 15% annual growth (rough S&P 500 equivalent for diversified portfolios).
    Used for the Greed Clock feature.
    """
    annual_growth = net_worth_billions * 1_000_000_000 * (growth_rate_pct / 100)
    per_second = annual_growth / (365.25 * 24 * 3600)
    return per_second


def _format_large_number(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
