"""
Export the computed dataset to a single static JSON the frontend ships with,
so the site needs no running backend.

This spins up a throwaway in-memory-ish SQLite DB, seeds it, computes greed
scores, then drives the real API endpoints in-process (via TestClient) so the
exported shapes are identical to what the live API returned. The output is
written to frontend/src/data/greed-data.json.

Run with:  python -m data.export_static
Re-run and commit the JSON whenever you update the seed data.
"""
import json
import os
import tempfile
from datetime import datetime, timezone

# DATABASE_URL must be set before importing app.database (engine is built at
# import time). Use a fresh temp DB so exports are deterministic and never
# depend on a leftover greed_index.db.
_tmp_db = os.path.join(tempfile.mkdtemp(), "export.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db}"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_PATH = os.path.join(REPO_ROOT, "frontend", "src", "data", "greed-data.json")


def main():
    from data.seed import seed
    seed()  # init_db + load seed json + compute & save scores

    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    leaderboard = client.get("/api/leaderboard?limit=200").json()
    stats = client.get("/api/stats").json()

    billionaires = {}
    for item in leaderboard["billionaires"]:
        slug = item["slug"]
        resp = client.get(f"/api/billionaires/{slug}")
        resp.raise_for_status()
        billionaires[slug] = resp.json()

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "leaderboard": leaderboard,
        "stats": stats,
        "billionaires": billionaires,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)

    kb = os.path.getsize(OUT_PATH) / 1024
    print(f"Wrote {len(billionaires)} billionaires to {OUT_PATH} ({kb:.0f} KB)")


if __name__ == "__main__":
    main()
