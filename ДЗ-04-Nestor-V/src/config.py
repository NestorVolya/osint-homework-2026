from pathlib import Path

START_URL = "https://risu.ua/novini_t1"
TARGET_DOMAIN = "risu.ua"
MAX_PAGES = 15

BASE_DIR = Path("/app")
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
NORMALIZED_DIR = DATA_DIR / "normalized"

METRICS_PORT = 8000
SCHEDULE_INTERVAL_MINUTES = 60

# CSS selectors for risu.ua
ARTICLE_LINK_SELECTORS = [
    "h2 a[href]",
    ".news-title a[href]",
    "article a[href]",
]
TITLE_SELECTORS = ["h1", ".article-title", ".entry-title"]
CONTENT_SELECTORS = [".article-body", ".entry-content", ".content", "article"]
DATE_SELECTORS = ["time[datetime]", ".article-date", ".date", ".publish-date"]
AUTHOR_SELECTORS = [".article-author", ".author", ".byline"]
TAG_SELECTORS = [".tag", ".category a", ".tags a"]
