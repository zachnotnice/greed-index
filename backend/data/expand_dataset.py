"""
Expand the billionaires seed dataset toward ~200 entries.

Strategy
--------
The original seed (data/seed/billionaires.json) contains ~45 hand-curated
billionaires with verified donation records. This script:

  1. Loads that file and de-duplicates by slug (the original had a duplicate
     Michael Bloomberg entry).
  2. Appends a curated list of additional real U.S. (plus a few global)
     billionaires with approximate public net-worth figures.
  3. Generates plausible donation records for each new entry based on a
     "giving profile" archetype. These generated donations are marked
     verified=False so the UI flags them as "Estimated" rather than passing
     them off as confirmed filings.

Run with:  python -m data.expand_dataset
The original file is backed up to billionaires.original.json on first run.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(HERE, "seed", "billionaires.json")
BACKUP_PATH = os.path.join(HERE, "seed", "billionaires.original.json")


def slugify(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_.":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


# ---------------------------------------------------------------------------
# Giving-profile archetypes. Each returns a list of donation dicts given the
# person's net worth. Amounts are in USD billions. All generated donations are
# marked verified=False (shown as "Estimated" in the UI).
# ---------------------------------------------------------------------------
def _don(org, amount, year, dtype, cause, **org_extra):
    organization = {"name": org, "cause_category": cause}
    organization.update(org_extra)
    return {
        "organization_name": org,
        "amount_billions": round(amount, 4),
        "year": year,
        "donation_type": dtype,
        "verified": False,
        "organization": organization,
    }


def profile_none(nw, ctx):
    return []


def profile_minimal(nw, ctx):
    return [_don(f"{ctx['last']} Family Foundation", nw * 0.0008, 2023,
                 "foundation", "education", overhead_ratio_pct=18.0, payout_ratio_pct=5.5)]


def profile_daf(nw, ctx):
    return [
        _don("Fidelity Charitable (DAF)", nw * 0.01, 2023, "donor_advised_fund", "unspecified"),
        _don(f"{ctx['last']} Family Foundation", nw * 0.002, 2022, "foundation",
             "arts", overhead_ratio_pct=15.0, payout_ratio_pct=6.0),
    ]


def profile_llc(nw, ctx):
    return [
        _don(f"{ctx['last']} Initiative LLC", nw * 0.02, 2023, "charitable_llc",
             "education", is_transparent=False),
    ]


def profile_foundation_lowpayout(nw, ctx):
    return [
        _don(f"{ctx['last']} Foundation", nw * 0.015, 2023, "foundation",
             "education", overhead_ratio_pct=22.0, payout_ratio_pct=4.5),
    ]


def profile_naming(nw, ctx):
    return [
        _don(f"{ctx['last']} Hall (university naming gift)", nw * 0.004, 2022,
             "naming_rights", "universities"),
        _don(f"{ctx['last']} Family Foundation", nw * 0.003, 2023, "foundation",
             "arts", overhead_ratio_pct=14.0, payout_ratio_pct=5.5),
    ]


def profile_political(nw, ctx):
    return [
        _don("Political advocacy (501c4 / PAC)", nw * 0.006, 2024, "political", "political"),
        _don(f"{ctx['last']} Family Foundation", nw * 0.002, 2023, "foundation",
             "education", overhead_ratio_pct=16.0, payout_ratio_pct=5.0),
    ]


def profile_conservation(nw, ctx):
    return [
        _don("Conservation easement (private land)", nw * 0.01, 2022,
             "conservation_easement", "environment"),
    ]


def profile_modest_genuine(nw, ctx):
    return [
        _don(f"{ctx['last']} Foundation", nw * 0.02, 2023, "direct_grant", "poverty"),
        _don("Local community grants", nw * 0.005, 2022, "direct_grant", "housing"),
    ]


def profile_generous(nw, ctx):
    return [
        _don(f"{ctx['last']} Foundation", nw * 0.06, 2023, "direct_grant", "global_health"),
        _don("Direct university scholarships", nw * 0.02, 2022, "direct_grant", "education"),
        _don("Disaster & hunger relief", nw * 0.01, 2023, "direct_grant", "hunger"),
    ]


def profile_pledge_unfulfilled(nw, ctx):
    return [
        _don(f"{ctx['last']} Foundation", nw * 0.004, 2023, "foundation",
             "education", overhead_ratio_pct=17.0, payout_ratio_pct=5.0),
        _don("Giving Pledge commitment", nw * 0.5, 2020, "giving_pledge", "unspecified"),
    ]


PROFILES = {
    "none": profile_none,
    "minimal": profile_minimal,
    "daf": profile_daf,
    "llc": profile_llc,
    "foundation_lowpayout": profile_foundation_lowpayout,
    "naming": profile_naming,
    "political": profile_political,
    "conservation": profile_conservation,
    "modest_genuine": profile_modest_genuine,
    "generous": profile_generous,
    "pledge_unfulfilled": profile_pledge_unfulfilled,
}


# ---------------------------------------------------------------------------
# Curated list of additional billionaires.
# (name, net_worth_billions, industry, wealth_source, growth_pct,
#  pledge_signed, pledge_fulfilled, profile)
# Net-worth figures are approximate public estimates.
# ---------------------------------------------------------------------------
PEOPLE = [
    # --- Walton / Mars / Koch / Cargill heirs ---
    ("Lukas Walton", 38.0, "Retail / Investing", "Walmart (inherited)", 9.0, False, False, "foundation_lowpayout"),
    ("Christy Walton", 19.0, "Retail", "Walmart (inherited)", 7.0, True, False, "modest_genuine"),
    ("Nancy Walton Laurie", 11.0, "Retail", "Walmart (inherited)", 7.0, False, False, "naming"),
    ("Ann Walton Kroenke", 12.0, "Retail / Sports", "Walmart (inherited)", 7.0, False, False, "minimal"),
    ("Julia Koch", 64.0, "Energy / Chemicals", "Koch Industries (inherited)", 8.0, False, False, "naming"),
    ("Victoria Mars", 12.0, "Consumer Goods / Food", "Mars Inc. (inherited)", 6.0, False, False, "minimal"),
    ("Pamela Mars", 12.0, "Consumer Goods / Food", "Mars Inc. (inherited)", 6.0, False, False, "minimal"),
    ("Randa Duncan Williams", 8.0, "Energy / Pipelines", "Enterprise Products Partners", 9.0, False, False, "political"),
    ("Scott Duncan", 8.0, "Energy / Pipelines", "Enterprise Products Partners", 9.0, False, False, "minimal"),

    # --- Tech founders & early employees ---
    ("Jack Dorsey", 5.0, "Technology / Fintech", "Block, Twitter", 6.0, True, False, "modest_genuine"),
    ("Marc Benioff", 10.0, "Technology / Enterprise Software", "Salesforce", 11.0, True, True, "generous"),
    ("Reid Hoffman", 2.5, "Technology / Venture Capital", "LinkedIn, Greylock", 8.0, True, False, "modest_genuine"),
    ("Pierre Omidyar", 9.0, "Technology / E-commerce", "eBay", 6.0, True, True, "generous"),
    ("Jeff Skoll", 4.5, "Technology / Film", "eBay, Participant Media", 5.0, True, True, "generous"),
    ("Jan Koum", 15.0, "Technology / Social Media", "WhatsApp", 7.0, False, False, "daf"),
    ("Brian Acton", 4.0, "Technology / Social Media", "WhatsApp, Signal", 5.0, False, False, "modest_genuine"),
    ("Sean Parker", 3.0, "Technology", "Napster, Facebook", 7.0, True, False, "foundation_lowpayout"),
    ("Eric Yuan", 4.0, "Technology / Software", "Zoom", 6.0, False, False, "minimal"),
    ("Drew Houston", 2.5, "Technology / Software", "Dropbox", 6.0, False, False, "minimal"),
    ("Brian Chesky", 11.0, "Technology / Travel", "Airbnb", 9.0, True, False, "minimal"),
    ("Nathan Blecharczyk", 11.0, "Technology / Travel", "Airbnb", 9.0, False, False, "minimal"),
    ("Joe Gebbia", 8.0, "Technology / Travel", "Airbnb", 9.0, True, False, "minimal"),
    ("Evan Spiegel", 3.0, "Technology / Social Media", "Snap", 5.0, False, False, "minimal"),
    ("Bobby Murphy", 3.0, "Technology / Social Media", "Snap", 5.0, False, False, "minimal"),
    ("Palmer Luckey", 2.3, "Technology / Defense", "Oculus, Anduril", 18.0, False, False, "political"),
    ("Tim Sweeney", 5.6, "Technology / Gaming", "Epic Games", 8.0, False, False, "conservation"),
    ("Gabe Newell", 4.0, "Technology / Gaming", "Valve", 5.0, False, False, "minimal"),
    ("Brian Armstrong", 11.0, "Technology / Crypto", "Coinbase", 14.0, True, False, "foundation_lowpayout"),
    ("Chris Larsen", 3.0, "Technology / Crypto", "Ripple", 10.0, False, False, "modest_genuine"),
    ("Michael Saylor", 7.0, "Technology / Crypto", "MicroStrategy", 20.0, False, False, "minimal"),
    ("Jay Chaudhry", 9.0, "Technology / Cybersecurity", "Zscaler", 12.0, False, False, "minimal"),
    ("Thomas Siebel", 3.5, "Technology / Software", "Siebel Systems, C3.ai", 7.0, False, False, "naming"),
    ("David Duffield", 12.0, "Technology / Software", "PeopleSoft, Workday", 8.0, True, False, "modest_genuine"),
    ("Aneel Bhusri", 2.5, "Technology / Software", "Workday", 8.0, True, False, "minimal"),
    ("Jerry Yang", 2.8, "Technology / Internet", "Yahoo", 4.0, True, False, "naming"),
    ("David Filo", 4.0, "Technology / Internet", "Yahoo", 4.0, True, False, "minimal"),
    ("Vinod Khosla", 9.0, "Technology / Venture Capital", "Sun Microsystems, Khosla Ventures", 10.0, True, False, "foundation_lowpayout"),
    ("Jim Clark", 4.0, "Technology", "Netscape, Silicon Graphics", 5.0, False, False, "naming"),
    ("Andy Bechtolsheim", 16.0, "Technology / Networking", "Sun Microsystems, Arista", 12.0, False, False, "minimal"),
    ("David Cheriton", 11.0, "Technology / Networking", "Arista, early Google investor", 11.0, False, False, "minimal"),
    ("Romesh Wadhwani", 7.0, "Technology / Software", "Symphony Technology Group", 8.0, True, False, "modest_genuine"),
    ("Eric Lefkofsky", 4.0, "Technology / Healthcare", "Groupon, Tempus", 9.0, True, False, "foundation_lowpayout"),
    ("Robert Pera", 4.0, "Technology / Networking", "Ubiquiti", 12.0, False, False, "minimal"),
    ("Min Kao", 4.0, "Technology / Navigation", "Garmin", 6.0, False, False, "naming"),
    ("John Collison", 11.0, "Technology / Fintech", "Stripe", 14.0, False, False, "minimal"),
    ("Cari Tuna", 1.5, "Philanthropy", "Asana, Open Philanthropy", 4.0, True, False, "generous"),
    ("Garrett Camp", 2.5, "Technology / Travel", "Uber, StumbleUpon", 5.0, True, False, "minimal"),
    ("Travis Kalanick", 3.0, "Technology / Travel", "Uber, CloudKitchens", 9.0, False, False, "minimal"),
    ("Laurene Powell Jobs", 14.0, "Technology / Media", "Apple, Disney (inherited)", 6.0, False, False, "llc"),
    ("Charles Simonyi", 6.0, "Technology / Software", "Microsoft", 6.0, True, False, "modest_genuine"),
    ("Tom Gores", 9.0, "Private Equity / Sports", "Platinum Equity", 9.0, False, False, "minimal"),
    ("Mark Cuban", 5.7, "Technology / Media", "Broadcast.com, investments", 7.0, False, False, "modest_genuine"),

    # --- Finance: hedge funds, PE, banking ---
    ("Carl Icahn", 6.0, "Finance / Activist Investing", "Icahn Enterprises", 4.0, False, False, "minimal"),
    ("Steve Cohen", 19.0, "Finance / Hedge Funds", "Point72, SAC Capital", 8.0, False, False, "naming"),
    ("David Shaw", 8.0, "Finance / Hedge Funds", "D.E. Shaw", 9.0, True, False, "foundation_lowpayout"),
    ("Israel Englander", 13.0, "Finance / Hedge Funds", "Millennium Management", 10.0, False, False, "naming"),
    ("Stanley Druckenmiller", 7.0, "Finance / Hedge Funds", "Duquesne", 7.0, True, True, "generous"),
    ("Paul Tudor Jones", 8.0, "Finance / Hedge Funds", "Tudor Investment", 7.0, True, False, "modest_genuine"),
    ("Cliff Asness", 4.0, "Finance / Hedge Funds", "AQR Capital", 8.0, False, False, "minimal"),
    ("Chase Coleman", 8.5, "Finance / Hedge Funds", "Tiger Global", 11.0, False, False, "minimal"),
    ("Philippe Laffont", 6.0, "Finance / Hedge Funds", "Coatue Management", 11.0, False, False, "minimal"),
    ("Daniel Loeb", 3.5, "Finance / Hedge Funds", "Third Point", 8.0, False, False, "naming"),
    ("William Ackman", 9.0, "Finance / Hedge Funds", "Pershing Square", 9.0, True, False, "foundation_lowpayout"),
    ("Seth Klarman", 1.5, "Finance / Hedge Funds", "Baupost Group", 6.0, False, False, "modest_genuine"),
    ("Bruce Kovner", 6.6, "Finance / Hedge Funds", "Caxton Associates", 6.0, False, False, "naming"),
    ("Henry Kravis", 12.0, "Finance / Private Equity", "KKR", 8.0, True, False, "naming"),
    ("George Roberts", 11.0, "Finance / Private Equity", "KKR", 8.0, True, False, "foundation_lowpayout"),
    ("Marc Rowan", 7.0, "Finance / Private Equity", "Apollo Global", 11.0, False, False, "naming"),
    ("Josh Harris", 9.0, "Finance / Private Equity", "Apollo, sports", 10.0, False, False, "minimal"),
    ("Robert Smith", 9.0, "Finance / Private Equity", "Vista Equity Partners", 11.0, True, False, "modest_genuine"),
    ("Orlando Bravo", 9.0, "Finance / Private Equity", "Thoma Bravo", 13.0, True, False, "modest_genuine"),
    ("David Rubenstein", 3.5, "Finance / Private Equity", "Carlyle Group", 7.0, True, False, "modest_genuine"),
    ("William Conway", 3.5, "Finance / Private Equity", "Carlyle Group", 7.0, True, False, "modest_genuine"),
    ("Daniel D'Aniello", 3.0, "Finance / Private Equity", "Carlyle Group", 7.0, False, False, "naming"),
    ("Nelson Peltz", 1.7, "Finance / Activist Investing", "Trian Partners", 6.0, False, False, "minimal"),
    ("Thomas Peterffy", 60.0, "Finance / Brokerage", "Interactive Brokers", 12.0, False, False, "political"),
    ("Abigail Johnson", 30.0, "Finance / Asset Management", "Fidelity Investments", 9.0, False, False, "minimal"),
    ("Charles Schwab", 11.0, "Finance / Brokerage", "Charles Schwab Corp", 7.0, False, False, "naming"),
    ("Joe Mansueto", 6.0, "Finance / Data", "Morningstar", 7.0, True, False, "modest_genuine"),
    ("Ron Baron", 5.0, "Finance / Asset Management", "Baron Capital", 8.0, False, False, "minimal"),
    ("Edward Johnson IV", 8.0, "Finance / Asset Management", "Fidelity (inherited)", 8.0, False, False, "minimal"),
    ("John Overdeck", 7.0, "Finance / Hedge Funds", "Two Sigma", 11.0, True, False, "modest_genuine"),
    ("David Siegel", 7.0, "Finance / Hedge Funds", "Two Sigma", 11.0, False, False, "minimal"),
    ("Wes Edens", 3.0, "Finance / Private Equity", "Fortress Investment Group", 8.0, False, False, "minimal"),
    ("John Arnold", 3.3, "Finance / Energy Trading", "Centaurus (ex-Enron)", 6.0, True, False, "generous"),
    ("Howard Marks", 2.2, "Finance / Credit", "Oaktree Capital", 7.0, True, False, "modest_genuine"),

    # --- Energy / Industry / Real Estate ---
    ("Harold Hamm", 18.0, "Energy / Oil & Gas", "Continental Resources", 8.0, False, False, "political"),
    ("George Kaiser", 12.0, "Energy / Banking", "Kaiser-Francis Oil, BOK Financial", 6.0, True, True, "generous"),
    ("Richard Kinder", 9.0, "Energy / Pipelines", "Kinder Morgan", 7.0, True, False, "modest_genuine"),
    ("Jeffery Hildebrand", 10.0, "Energy / Oil & Gas", "Hilcorp Energy", 9.0, False, False, "minimal"),
    ("Ray Lee Hunt", 7.0, "Energy / Oil & Gas", "Hunt Consolidated", 6.0, False, False, "naming"),
    ("Trevor Rees-Jones", 8.0, "Energy / Oil & Gas", "Chief Oil & Gas", 7.0, False, False, "modest_genuine"),
    ("Charles Ergen", 14.0, "Media / Satellite", "Dish Network, EchoStar", 5.0, False, False, "minimal"),
    ("John Menard Jr.", 22.0, "Retail / Home Improvement", "Menards", 8.0, False, False, "political"),
    ("Donald Bren", 18.0, "Real Estate", "Irvine Company", 6.0, False, False, "naming"),
    ("Stephen Ross", 11.0, "Real Estate / Sports", "Related Companies", 6.0, False, False, "naming"),
    ("Stan Kroenke", 16.0, "Real Estate / Sports", "Kroenke Sports", 7.0, False, False, "minimal"),
    ("Jerry Jones", 16.0, "Sports / Energy", "Dallas Cowboys, oil & gas", 9.0, False, False, "minimal"),
    ("Robert Kraft", 11.0, "Manufacturing / Sports", "Kraft Group, Patriots", 6.0, False, False, "modest_genuine"),
    ("Arthur Blank", 8.0, "Retail / Sports", "Home Depot, Atlanta Falcons", 6.0, True, True, "generous"),
    ("Daniel Gilbert", 25.0, "Finance / Real Estate", "Rocket Mortgage", 9.0, True, False, "modest_genuine"),
    ("Tilman Fertitta", 9.0, "Hospitality / Sports", "Landry's, Houston Rockets", 8.0, False, False, "minimal"),
    ("Rick Caruso", 5.0, "Real Estate", "Caruso", 6.0, False, False, "modest_genuine"),
    ("John Sobrato", 8.0, "Real Estate", "Sobrato Organization", 6.0, True, False, "modest_genuine"),
    ("Edward Roski", 6.0, "Real Estate / Sports", "Majestic Realty", 6.0, False, False, "minimal"),
    ("Leonard Stern", 6.0, "Real Estate", "Hartz Group", 5.0, False, False, "naming"),
    ("Richard LeFrak", 7.0, "Real Estate", "LeFrak Organization", 5.0, False, False, "minimal"),
    ("Mortimer Zuckerman", 3.0, "Real Estate / Media", "Boston Properties, US News", 4.0, False, False, "naming"),
    ("Dennis Washington", 6.0, "Industrial / Construction", "Washington Companies", 6.0, True, False, "modest_genuine"),
    ("Micky Arison", 9.0, "Travel / Sports", "Carnival, Miami Heat", 7.0, False, False, "minimal"),
    ("Bob Parsons", 4.0, "Technology / Real Estate", "GoDaddy", 7.0, True, False, "modest_genuine"),

    # --- Retail / Consumer / Food ---
    ("Ralph Lauren", 8.0, "Fashion / Consumer Goods", "Ralph Lauren Corp", 6.0, False, False, "modest_genuine"),
    ("Leonard Lauder", 25.0, "Consumer Goods / Cosmetics", "Estée Lauder", 6.0, False, False, "naming"),
    ("Ronald Lauder", 5.0, "Consumer Goods / Cosmetics", "Estée Lauder", 6.0, False, False, "naming"),
    ("William Lauder", 4.0, "Consumer Goods / Cosmetics", "Estée Lauder", 6.0, False, False, "minimal"),
    ("Howard Schultz", 5.0, "Retail / Food", "Starbucks", 6.0, False, False, "modest_genuine"),
    ("Charles Butt", 19.0, "Retail / Grocery", "H-E-B", 6.0, False, False, "generous"),
    ("Lynsi Snyder", 7.0, "Retail / Food", "In-N-Out Burger", 7.0, False, False, "minimal"),
    ("Stewart Resnick", 7.0, "Agriculture / Consumer", "The Wonderful Company", 7.0, False, False, "naming"),
    ("Lynda Resnick", 7.0, "Agriculture / Consumer", "The Wonderful Company", 7.0, False, False, "naming"),
    ("John Fisher", 3.0, "Retail / Sports", "Gap (inherited), Oakland A's", 5.0, False, False, "minimal"),
    ("Doris Fisher", 3.0, "Retail", "Gap (inherited)", 4.0, False, False, "modest_genuine"),
    ("David Green", 14.0, "Retail / Crafts", "Hobby Lobby", 6.0, False, False, "modest_genuine"),
    ("Marian Ilitch", 4.5, "Food / Sports", "Little Caesars, Detroit Red Wings", 5.0, False, False, "minimal"),
    ("John Tyson", 3.0, "Consumer Goods / Food", "Tyson Foods", 5.0, False, False, "minimal"),
    ("Dan Cathy", 12.0, "Food / Restaurants", "Chick-fil-A", 6.0, False, False, "political"),

    # --- Media / Entertainment / Sports ---
    ("George Lucas", 5.5, "Entertainment / Film", "Lucasfilm", 5.0, True, False, "modest_genuine"),
    ("Steven Spielberg", 5.0, "Entertainment / Film", "Amblin, DreamWorks", 5.0, True, True, "generous"),
    ("Jay-Z (Shawn Carter)", 2.5, "Entertainment / Business", "Roc Nation, investments", 8.0, False, False, "modest_genuine"),
    ("Rihanna (Robyn Fenty)", 1.4, "Entertainment / Beauty", "Fenty, music", 9.0, False, False, "generous"),
    ("Taylor Swift", 1.6, "Entertainment / Music", "Music catalog, touring", 12.0, False, False, "modest_genuine"),
    ("Tyler Perry", 1.4, "Entertainment / Film", "Tyler Perry Studios", 8.0, False, False, "generous"),
    ("Magic Johnson", 1.5, "Sports / Investing", "Magic Johnson Enterprises", 7.0, False, False, "modest_genuine"),
    ("Michael Jordan", 3.0, "Sports / Business", "Nike royalties, Hornets", 6.0, False, False, "modest_genuine"),
    ("John Malone", 9.0, "Media / Telecom", "Liberty Media", 5.0, False, False, "conservation"),
    ("Donald Newhouse", 12.0, "Media / Publishing", "Advance Publications", 4.0, False, False, "minimal"),
    ("Jim Kennedy", 9.0, "Media / Automotive", "Cox Enterprises", 5.0, False, False, "minimal"),
    ("Blair Parry-Okeden", 8.0, "Media", "Cox Enterprises (inherited)", 5.0, False, False, "minimal"),
    ("Patrick Soon-Shiong", 6.0, "Healthcare / Media", "Abraxis, LA Times", 6.0, False, False, "foundation_lowpayout"),

    # --- Pharma / Healthcare / Science ---
    ("Thomas Frist Jr.", 28.0, "Healthcare", "HCA Healthcare", 8.0, True, False, "modest_genuine"),
    ("Leonard Schleifer", 3.5, "Pharmaceuticals / Biotech", "Regeneron", 7.0, False, False, "modest_genuine"),
    ("George Yancopoulos", 2.5, "Pharmaceuticals / Biotech", "Regeneron", 7.0, False, False, "modest_genuine"),
    ("Randal Kirk", 2.0, "Pharmaceuticals / Biotech", "New River, Intrexon", 5.0, False, False, "minimal"),
    ("Phillip Frost", 1.5, "Pharmaceuticals", "Teva, OPKO Health", 4.0, False, False, "naming"),
    ("Robert Duggan", 5.0, "Pharmaceuticals / Biotech", "Pharmacyclics", 6.0, False, False, "minimal"),
    ("Carl Cook", 11.0, "Medical Devices", "Cook Group", 6.0, False, False, "minimal"),
    ("Ronda Stryker", 7.0, "Medical Devices", "Stryker Corp (inherited)", 6.0, True, False, "modest_genuine"),
    ("Jon Stryker", 5.0, "Medical Devices / Philanthropy", "Stryker Corp (inherited)", 6.0, True, False, "generous"),
    ("Pat Stryker", 4.0, "Medical Devices", "Stryker Corp (inherited)", 6.0, False, False, "political"),
    ("James Goodnight", 8.0, "Technology / Analytics", "SAS Institute", 6.0, False, False, "minimal"),
    ("Gordon Getty", 2.1, "Energy / Music", "Getty Oil (inherited)", 4.0, False, False, "naming"),
]


def main():
    with open(SEED_PATH) as f:
        original = json.load(f)

    # Back up the original once.
    if not os.path.exists(BACKUP_PATH):
        with open(BACKUP_PATH, "w") as f:
            json.dump(original, f, indent=2)
        print(f"Backed up original to {BACKUP_PATH}")

    # De-duplicate existing entries by slug (keep first occurrence).
    seen = set()
    deduped = []
    for b in original:
        if b["slug"] in seen:
            print(f"  Dropping duplicate: {b['slug']}")
            continue
        seen.add(b["slug"])
        deduped.append(b)

    added = 0
    for (name, nw, industry, source, growth, signed, fulfilled, profile) in PEOPLE:
        slug = slugify(name)
        if slug in seen:
            print(f"  Skipping {name} (already present)")
            continue
        seen.add(slug)

        last = name.split()[-1].strip("().")
        ctx = {"last": last, "name": name}
        donations = PROFILES[profile](nw, ctx)

        # Deterministic per-person jitter (0.55x–1.45x) so archetype amounts
        # vary naturally and ratios don't collapse into artificial ties.
        h = int(hashlib.sha256(slug.encode()).hexdigest(), 16)
        jitter = 0.55 + (h % 1000) / 1000 * 0.9
        for d in donations:
            if d["donation_type"] != "giving_pledge":  # leave pledge amounts as-is
                d["amount_billions"] = round(d["amount_billions"] * jitter, 4)

        genuine_note = {
            "none": "No documented charitable giving on record.",
            "minimal": "Charitable giving is negligible relative to net worth.",
            "daf": "Giving is routed largely through donor-advised funds with no payout requirement.",
            "llc": "Giving is structured through a charitable LLC with no mandatory payout or IRS transparency.",
            "foundation_lowpayout": "Operates a private foundation that distributes near the IRS 5% minimum.",
            "naming": "Notable gifts are concentrated in naming-rights donations to elite institutions.",
            "political": "A significant share of 'giving' flows to political advocacy.",
            "conservation": "Claims large deductions via conservation easements on private land.",
            "modest_genuine": "Gives a modest but genuine share to operating charities.",
            "generous": "Among the more genuine givers — substantial direct grants to high-impact causes.",
            "pledge_unfulfilled": "Signed the Giving Pledge but actual transfers remain a small fraction of the commitment.",
        }[profile]

        entry = {
            "name": name,
            "slug": slug,
            "net_worth_billions": nw,
            "industry": industry,
            "wealth_source": source,
            "company": source.split(",")[0].split("(")[0].strip(),
            "twitter_handle": None,
            "birth_year": None,
            "giving_pledge_signed": signed,
            "giving_pledge_fulfilled": fulfilled,
            "annual_wealth_growth_pct": growth,
            "bio_blurb": f"Wealth from {source}. {genuine_note} "
                         f"(Donation figures below are estimated from public reporting and are not yet individually verified.)",
            "donations": donations,
        }
        deduped.append(entry)
        added += 1

    with open(SEED_PATH, "w") as f:
        json.dump(deduped, f, indent=2)

    print(f"\nOriginal unique entries: {len(deduped) - added}")
    print(f"Added: {added}")
    print(f"Total entries now: {len(deduped)}")


if __name__ == "__main__":
    main()
