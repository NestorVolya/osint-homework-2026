import threading
from prometheus_client import Counter, Gauge, Histogram, start_http_server

pages_crawled = Counter(
    "pages_crawled_total",
    "Total pages successfully crawled",
    ["worker"],
)
pages_failed = Counter(
    "pages_failed_total",
    "Total pages that failed to crawl",
    ["worker"],
)
content_bytes = Histogram(
    "page_content_bytes",
    "Size of extracted page content in bytes",
    ["worker"],
    buckets=[500, 1000, 5000, 10000, 50000, 100000],
)
last_crawl_ts = Gauge("last_crawl_timestamp", "Unix timestamp of last crawl")
success_rate = Gauge("success_rate", "Ratio of successful crawls", ["worker"])

_totals: dict[str, dict] = {}


def record_success(worker: str, content_len: int = 0) -> None:
    pages_crawled.labels(worker=worker).inc()
    content_bytes.labels(worker=worker).observe(content_len)
    last_crawl_ts.set_to_current_time()
    _update_rate(worker)


def record_failure(worker: str) -> None:
    pages_failed.labels(worker=worker).inc()
    _update_rate(worker)


def _update_rate(worker: str) -> None:
    ok = pages_crawled.labels(worker=worker)._value.get()
    fail = pages_failed.labels(worker=worker)._value.get()
    total = ok + fail
    success_rate.labels(worker=worker).set(ok / total if total else 0)


def start_metrics_server(port: int) -> None:
    thread = threading.Thread(target=start_http_server, args=(port,), daemon=True)
    thread.start()
