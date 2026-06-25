"""
CLI entry point and pipeline orchestrator.

Usage:
    python -m pipeline.run --seed "Ім'я Прізвище" --seed_type fullname
    python -m pipeline.run --seed "@handle" --seed_type nickname --dry-run
"""

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from pipeline.gates.input_gate import validate_seed, detect_seed_type
from pipeline.gates.budget_gate import BudgetTracker, load_settings, BudgetExceeded
from pipeline.storage.db import Database
from pipeline.storage.archive import create_run_dir, zip_run
from pipeline.collect import run_collect
from pipeline.account_discovery import run_account_discovery
from pipeline.account_graph import run_account_graph
from pipeline.enrich_timeline import run_enrich_timeline
from pipeline.enrich_statements import run_enrich_statements
from pipeline.detect_contradictions import run_detect_contradictions
from pipeline.enrich_network import run_enrich_network
from pipeline.geoclusters import run_geoclusters
from pipeline.report import run_report
from pipeline.quality_check import run_quality_check
from pipeline.report_md import run_report_md

BASE_DIR = Path(__file__).parent.parent

# Load .env from project root if present; override via DOTENV_PATH env variable
_dotenv_path = os.environ.get("DOTENV_PATH", str(BASE_DIR / ".env"))
load_dotenv(_dotenv_path, override=False)
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", str(BASE_DIR / "output")))
TEMPLATES_DIR = BASE_DIR / "templates"
DEFAULT_CONFIG = BASE_DIR / "config" / "settings.yaml"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="actor-osint-front pipeline")
    p.add_argument("--seed", required=True, help="Primary seed: nickname / email / fullname")
    p.add_argument("--seed_type", default="auto",
                   choices=["auto", "nickname", "email", "fullname"])
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--platform_hint", nargs="*", default=[])
    p.add_argument("--language_hint", nargs="*", default=["uk", "ru", "en"])
    p.add_argument("--time_window", default="")
    p.add_argument("--dry-run", action="store_true",
                   help="Init dirs and DB only, skip API calls")
    p.add_argument("--profile", default=None,
                   help="Path to benchmark profile YAML (default: ua_cultural_ru_sphere.yaml)")
    return p


def main():
    args = build_parser().parse_args()
    t0 = time.time()

    # --- Input gate ---
    seed_type = args.seed_type
    if seed_type == "auto":
        seed_type = detect_seed_type(args.seed)
        logger.info(f"auto-detected seed_type: {seed_type}")

    try:
        seed = validate_seed(args.seed, seed_type)
    except ValueError as e:
        logger.error(f"Input validation failed: {e}")
        sys.exit(1)

    # --- Budget gate ---
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Config not found: {config_path}")
        sys.exit(1)
    settings = load_settings(config_path)
    budget = BudgetTracker(settings)

    # --- Setup run dir + DB ---
    run_dir = create_run_dir(OUTPUT_DIR)
    db_path = run_dir / "artifacts" / "records.sqlite"
    db = Database(db_path)
    actor_id = str(uuid.uuid4())[:8]

    logger.info(f"Run dir: {run_dir}")
    logger.info(f"Seed: {seed!r} | type: {seed_type} | actor_id: {actor_id}")

    if args.dry_run:
        logger.info("dry-run mode: skipping API calls")
        db.close()
        logger.info(f"Output ready: {run_dir}")
        return

    max_runtime = budget.max_runtime

    def _check_runtime():
        elapsed = time.time() - t0
        if elapsed > max_runtime:
            raise RuntimeError(f"max_runtime_seconds={max_runtime} exceeded ({elapsed:.0f}s)")

    profile_path = Path(args.profile) if args.profile else (
        BASE_DIR / "benchmark_profiles" / "ua_cultural_ru_sphere.yaml"
    )

    # Load optional query_context from profile for same-name disambiguation
    query_context: list[str] = []
    try:
        import yaml as _yaml
        with open(profile_path, encoding="utf-8") as _f:
            _prof = _yaml.safe_load(_f)
        query_context = (_prof.get("context") or {}).get("query_context") or []
        if query_context:
            logger.info(f"query_context active: {query_context}")
    except Exception as _e:
        logger.debug(f"query_context load skipped: {_e}")

    # --- Pipeline ---
    try:
        collected, collect_meta = run_collect(
            seed=seed, actor_id=actor_id, seed_type=seed_type,
            db=db, run_dir=run_dir, budget=budget,
            language_hint=args.language_hint,
            platform_hint=args.platform_hint,
            time_window=args.time_window,
            query_context=query_context or None,
        )
        _check_runtime()

        run_account_discovery(
            seed=seed, actor_id=actor_id, seed_type=seed_type,
            db=db, run_dir=run_dir, budget=budget,
        )
        _check_runtime()

        run_account_graph(db=db, report_dir=run_dir / "report")

        run_enrich_timeline(actor_id=actor_id, db=db)
        _check_runtime()

        run_enrich_statements(actor_id=actor_id, db=db, budget=budget)
        _check_runtime()

        run_detect_contradictions(actor_id=actor_id, db=db, budget=budget, run_dir=run_dir)

        run_enrich_network(actor_id=actor_id, db=db, budget=budget)

        run_geoclusters(db=db)

        quality_report = run_quality_check(
            actor_id=actor_id, db=db,
            collect_meta=collect_meta,
            profile_path=profile_path,
        )
        (run_dir / "quality_report.json").write_text(
            json.dumps(quality_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        report_path = run_report(
            actor_id=actor_id, seed=seed,
            db=db, run_dir=run_dir, templates_dir=TEMPLATES_DIR,
            quality_report=quality_report,
        )

        run_report_md(
            quality_report=quality_report, seed=seed,
            run_dir=run_dir, actor_id=actor_id, run_id=run_dir.name,
        )

    except BudgetExceeded as e:
        logger.error(f"Budget exceeded: {e}")
        db.close()
        sys.exit(2)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        db.close()
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Pipeline error: {e}")
        db.close()
        sys.exit(1)

    db.close()

    zip_path = zip_run(run_dir)
    elapsed = time.time() - t0

    logger.info(f"Done in {elapsed:.1f}s")
    logger.info(f"Report:  {report_path}")
    logger.info(f"Archive: {zip_path}")


if __name__ == "__main__":
    main()
