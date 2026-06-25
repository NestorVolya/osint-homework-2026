"""
Live collect test - потребує реальних API-ключів.

Run:
    $env:DOTENV_PATH = "/path/to/secrets.env"
    .venv/Scripts/python.exe tests/test_collect_live.py
"""

import os
import sys
import json
import sqlite3
import tempfile
from pathlib import Path
from collections import Counter

from dotenv import load_dotenv

# Load keys
dotenv_path = os.environ.get("DOTENV_PATH", str(Path(__file__).parent.parent / ".env"))
load_dotenv(dotenv_path, override=True)

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.storage.db import Database
from pipeline.storage.archive import create_run_dir
from pipeline.gates.budget_gate import BudgetTracker, load_settings
from pipeline.collect import run_collect

SEED = "Олексій Чекаль"
SEED_TYPE = "fullname"
CONFIG = Path(__file__).parent.parent / "config" / "settings.yaml"


def check_keys():
    missing = []
    for k in ["EXA_API_KEY", "TAVILY_API_KEY"]:
        if not os.environ.get(k):
            missing.append(k)
    if missing:
        print(f"[!] Missing keys: {missing}")
        print(f"    Set DOTENV_PATH or add keys to .env")
        sys.exit(1)
    print(f"[+] Keys loaded: EXA={'***' if os.environ.get('EXA_API_KEY') else 'MISSING'}, "
          f"TAVILY={'***' if os.environ.get('TAVILY_API_KEY') else 'MISSING'}")


def inspect_raw(run_dir: Path):
    raw_dir = run_dir / "raw"
    json_files = list(raw_dir.glob("*.json"))
    print(f"\n--- raw/ ({len(json_files)} files) ---")
    for f in json_files:
        data = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(data, list):
            print(f"  {f.name}: {len(data)} results")
            if data:
                sample = data[0]
                keys = list(sample.keys())
                has_text = bool(sample.get("text") or sample.get("raw_content") or sample.get("content"))
                has_date = bool(sample.get("publishedDate") or sample.get("published_date"))
                print(f"    keys: {keys}")
                print(f"    has_text={has_text}, has_date={has_date}")
        else:
            print(f"  {f.name}: (non-list, keys={list(data.keys())[:5]})")


def inspect_db(db_path: Path, actor_id: str):
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT source_type, count(*) as n FROM sources GROUP BY source_type").fetchall()
    total = conn.execute("SELECT count(*) FROM sources").fetchone()[0]
    with_date = conn.execute("SELECT count(*) FROM sources WHERE date_raw IS NOT NULL AND date_raw != ''").fetchone()[0]
    with_text = conn.execute("SELECT count(*) FROM sources WHERE length(text) > 100").fetchone()[0]
    urls = conn.execute("SELECT url, source_type, date_raw FROM sources LIMIT 20").fetchall()
    conn.close()

    print(f"\n--- SQLite sources (total={total}) ---")
    print(f"  with date_raw: {with_date}/{total}")
    print(f"  with text>100: {with_text}/{total}")
    print(f"  by type: {dict(rows)}")
    print(f"\n  Top URLs:")
    for url, stype, date in urls:
        print(f"    [{stype}] {date or '—':12} {url[:80]}")

    return total


def run():
    check_keys()

    settings = load_settings(CONFIG)
    budget = BudgetTracker(settings)

    with tempfile.TemporaryDirectory(prefix="collect_live_") as tmp:
        run_dir = create_run_dir(Path(tmp))
        db_path = run_dir / "artifacts" / "records.sqlite"
        db = Database(db_path)
        actor_id = "live_test"

        print(f"\n[*] Seed: {SEED!r} ({SEED_TYPE})")
        print(f"[*] Run dir: {run_dir}")

        sources = run_collect(
            seed=SEED,
            actor_id=actor_id,
            seed_type=SEED_TYPE,
            db=db,
            run_dir=run_dir,
            budget=budget,
            language_hint=["uk", "ru", "en"],
        )

        db.close()

        inspect_raw(run_dir)
        total = inspect_db(db_path, actor_id)

        print(f"\n--- Summary ---")
        print(f"  Collected: {len(sources)} sources → SQLite: {total}")

        # Assertions
        ok = True
        if total < 5:
            print(f"  [FAIL] Expected ≥5 sources, got {total}")
            ok = False
        else:
            print(f"  [PASS] sources ≥5")

        raw_files = list((run_dir / "raw").glob("*.json"))
        if not raw_files:
            print(f"  [FAIL] No raw JSON files")
            ok = False
        else:
            print(f"  [PASS] raw/ has {len(raw_files)} files")

        if ok:
            print("\n[OK] collect.py passes live test")
        else:
            print("\n[FAIL] Issues found — see above")
            sys.exit(1)


if __name__ == "__main__":
    run()
