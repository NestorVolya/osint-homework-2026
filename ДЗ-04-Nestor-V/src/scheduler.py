"""
scheduler — запускає worker_html і normalize за розкладом (APScheduler).
Два jobs:
  1. crawl   — кожні SCHEDULE_INTERVAL_MINUTES хвилин
  2. normalize — через 5 хвилин після crawl
"""

import asyncio
import logging
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

import config
import worker_html
import normalize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("scheduler")


def job_crawl() -> None:
    log.info("Scheduler: запуск worker_html")
    asyncio.run(worker_html.run())
    log.info("Scheduler: worker_html завершено")


def job_normalize() -> None:
    log.info("Scheduler: запуск normalize")
    normalize.run()
    log.info("Scheduler: normalize завершено")


def main() -> None:
    log.info(
        "Scheduler стартує. Інтервал crawl: %d хв",
        config.SCHEDULE_INTERVAL_MINUTES,
    )

    # Run immediately on start
    job_crawl()
    job_normalize()

    scheduler = BlockingScheduler(timezone="Europe/Kyiv")

    scheduler.add_job(
        job_crawl,
        "interval",
        minutes=config.SCHEDULE_INTERVAL_MINUTES,
        id="crawl",
    )
    scheduler.add_job(
        job_normalize,
        "interval",
        minutes=config.SCHEDULE_INTERVAL_MINUTES,
        id="normalize",
        # Offset by 5 minutes after crawl
        start_date="2026-01-01 00:05:00",
    )

    log.info("Scheduler запущено. Ctrl+C для зупинки.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler зупинено")


if __name__ == "__main__":
    main()
