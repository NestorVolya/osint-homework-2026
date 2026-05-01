"""
worker_html — базовий HTML-воркер для risu.ua.
Збирає список статей з /uk/news/, потім скрапить кожну статтю.
Зберігає сирий JSON у data/raw/.
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
log = logging.getLogger("worker-html")

WORKER = "html"

LIST_SCHEMA = {
    "name": "ArticleLinks",
    "baseSelector": "article, .news-item, .post-item, h2, h3",
    "fields": [
        {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
        {"name": "title", "selector": "a", "type": "text"},
    ],
}

ARTICLE_SCHEMA = {
    "name": "Article",
    "baseSelector": "body",
    "fields": [
        {"name": "title", "selector": "h1", "type": "text"},
        {"name": "date", "selector": "time", "type": "attribute", "attribute": "datetime"},
        {"name": "date_text", "selector": "time, .date, .publish-date", "type": "text"},
        {"name": "author", "selector": ".author, .byline, .article-author", "type": "text"},
        {"name": "tags", "selector": ".tag, .tags a, .category a", "type": "list"},
        {"name": "content", "selector": ".article-body, .entry-content, .content, article", "type": "text"},
    ],
}


def _slug(url: str) -> str:
    path = urlparse(url).path.strip("/").replace("/", "_")
    return re.sub(r"[^a-zA-Z0-9_\-]", "", path)[:80] or "page"


def _is_article_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.netloc and config.TARGET_DOMAIN not in parsed.netloc:
        return False
    # risu.ua article URLs end with _n<digits>
    return bool(re.search(r"_n\d+$", parsed.path))


def _save_raw(data: dict) -> Path:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    slug = _slug(data["url"])
    path = config.RAW_DIR / f"{slug}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


async def crawl_list(crawler: AsyncWebCrawler) -> list[str]:
    log.info("Збираю список статей з %s", config.START_URL)
    result = await crawler.arun(url=config.START_URL, config=CrawlerRunConfig(verbose=False))
    if not result.success:
        log.error("Не вдалося завантажити список: %s", result.error_message)
        metrics.record_failure(WORKER)
        return []

    # Use built-in link extractor — risu.ua article URLs end with _n<digits>
    links: list[str] = []
    for link_obj in result.links.get("internal", []):
        href = link_obj.get("href", "")
        if href and _is_article_url(href):
            links.append(href)

    unique = list(dict.fromkeys(links))
    log.info("Знайдено %d унікальних посилань на статті", len(unique))
    return unique[: config.MAX_PAGES]


async def crawl_article(crawler: AsyncWebCrawler, url: str) -> dict | None:
    log.info("Скрапинг статті: %s", url)
    run_cfg = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(ARTICLE_SCHEMA),
        verbose=False,
    )
    result = await crawler.arun(url=url, config=run_cfg)
    if not result.success:
        log.error("Помилка при скрапингу %s: %s", url, result.error_message)
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
    date_val = extracted.get("date") or extracted.get("date_text") or ""

    # Collect all internal links
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
            "date_raw": date_val,
            "content_length": len(content),
        },
    }

    path = _save_raw(raw)
    metrics.record_success(WORKER, len(content))
    log.info("Збережено → %s (%d chars)", path.name, len(content))
    return raw


async def run() -> None:
    metrics.start_metrics_server(config.METRICS_PORT)
    log.info("Метрики доступні на :%d/metrics", config.METRICS_PORT)

    browser_cfg = BrowserConfig(headless=True, verbose=False)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        urls = await crawl_list(crawler)
        if not urls:
            log.warning("Список статей порожній — перевір селектори")
            return

        for url in urls:
            await crawl_article(crawler, url)
            await asyncio.sleep(1)  # rate limiting

    log.info("Готово. Зібрано сторінок: %d", len(urls))


if __name__ == "__main__":
    asyncio.run(run())
