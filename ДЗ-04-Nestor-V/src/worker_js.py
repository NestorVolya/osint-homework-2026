"""
worker_js — JS-розширений воркер для risu.ua.
Відрізняється від worker_html:
  - явне очікування завантаження контенту (wait_for CSS)
  - dismiss cookie-банерів через js_code
  - затримка перед зчитуванням HTML (delay_before_return_html)
  - структурована екстракція через JsonCssExtractionStrategy з більшою деталізацією

Коли він потрібен: сторінки, де контент рендериться після JS (lazy-load, SPA-фрагменти).
На risu.ua це актуально для: галерей, вбудованих відео, динамічних коментарів.
"""

import asyncio
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

import config
import metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("worker-js")

WORKER = "js"

ARTICLE_SCHEMA = {
    "name": "ArticleDetailed",
    "baseSelector": "body",
    "fields": [
        {"name": "title", "selector": "h1", "type": "text"},
        {"name": "date", "selector": "time", "type": "attribute", "attribute": "datetime"},
        {"name": "date_text", "selector": "time, .date, .publish-date", "type": "text"},
        {"name": "author", "selector": ".author, .byline, .article-author", "type": "text"},
        {"name": "tags", "selector": ".tag, .tags a, .category a", "type": "list"},
        {"name": "content", "selector": ".article-body, .entry-content, .content, article", "type": "text"},
        {"name": "lead", "selector": ".lead, .article-lead, .intro", "type": "text"},
        {"name": "images", "selector": "article img", "type": "list"},
    ],
}

# JS snippet to dismiss common cookie banners
DISMISS_COOKIES_JS = """
(function() {
  const selectors = [
    '[id*="cookie"] button', '[class*="cookie"] button',
    '[id*="consent"] button', '[class*="consent"] button',
    '.accept-cookies', '#accept-cookies',
  ];
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) { el.click(); break; }
  }
})();
"""


def _slug(url: str) -> str:
    path = urlparse(url).path.strip("/").replace("/", "_")
    clean = re.sub(r"[^a-zA-Z0-9_\-]", "", path)[:80]
    return (clean or "page") + "_js"


def _save_raw(data: dict) -> Path:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    slug = _slug(data["url"])
    path = config.RAW_DIR / f"{slug}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _load_article_urls() -> list[str]:
    """Read article URLs already collected by worker_html."""
    urls = []
    if config.RAW_DIR.exists():
        for f in config.RAW_DIR.glob("*.json"):
            if f.name.endswith("_js.json"):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get("url"):
                    urls.append(data["url"])
            except (json.JSONDecodeError, KeyError):
                pass
    return urls


async def crawl_article_js(crawler: AsyncWebCrawler, url: str) -> dict | None:
    log.info("JS-скрапинг статті: %s", url)

    run_cfg = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(ARTICLE_SCHEMA),
        js_code=DISMISS_COOKIES_JS,
        wait_for="css:h1",
        delay_before_return_html=1.5,
        verbose=False,
    )

    result = await crawler.arun(url=url, config=run_cfg)
    if not result.success:
        log.error("Помилка JS-скрапингу %s: %s", url, result.error_message)
        metrics.record_failure(WORKER)
        return None

    extracted: dict = {}
    if result.extracted_content:
        try:
            items = json.loads(result.extracted_content)
            extracted = items[0] if items else {}
        except (json.JSONDecodeError, IndexError):
            pass

    title = extracted.get("title") or result.metadata.get("title", "")
    content = extracted.get("content") or result.markdown or ""

    internal_links = []
    if result.links:
        for link_obj in result.links.get("internal", []):
            href = link_obj.get("href", "")
            if href and config.TARGET_DOMAIN in href:
                internal_links.append(href)

    raw = {
        "url": url,
        "title": title.strip(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": config.TARGET_DOMAIN,
        "content": content.strip(),
        "links": internal_links[:20],
        "metadata": {
            "worker": WORKER,
            "author": (extracted.get("author") or "").strip(),
            "tags": extracted.get("tags") or [],
            "lead": (extracted.get("lead") or "").strip(),
            "date_raw": extracted.get("date") or extracted.get("date_text") or "",
            "content_length": len(content),
            "js_rendered": True,
        },
    }

    path = _save_raw(raw)
    metrics.record_success(WORKER, len(content))
    log.info("Збережено JS → %s (%d chars)", path.name, len(content))
    return raw


async def run() -> None:
    metrics.start_metrics_server(config.METRICS_PORT)
    log.info("JS-воркер запущено. Метрики на :%d/metrics", config.METRICS_PORT)

    urls = _load_article_urls()
    if not urls:
        log.warning("Немає URL у data/raw/ — спочатку запусти worker_html")
        return

    log.info("JS-обробка %d статей", len(urls))

    browser_cfg = BrowserConfig(headless=True, java_script_enabled=True, verbose=False)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for url in urls:
            await crawl_article_js(crawler, url)
            await asyncio.sleep(1.5)

    log.info("JS-воркер завершив роботу")


if __name__ == "__main__":
    asyncio.run(run())
