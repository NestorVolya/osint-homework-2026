"""
Gold standard benchmark: pipeline sources vs 167 Wikipedia footnotes (Чекаль).

Usage:
    python tests/benchmark_gold_standard.py [RUN_ZIP_OR_DB] [FOOTNOTES_MD]

Defaults:
    FOOTNOTES_MD — pass as second argument (local file with 167 Wikipedia source footnotes)
    RUN_ZIP_OR_DB — latest zip in output/ OR path to records.sqlite directly

Output:
    Per-class coverage table (L1=exact URL, L2=same domain)
    Weighted recall score
"""

import re
import sqlite3
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

# ── Domain → class mapping ────────────────────────────────────────────────────

DOMAIN_CLASS: dict[str, str] = {
    # A — UA / EN web
    "ksada.org": "A", "old.ksada.org": "A",
    "risu.ua": "A",
    "radiosvoboda.org": "A",
    "behance.net": "A", "www.behance.net": "A",
    "mkdu.com.ua": "A",
    "multilingual.com": "A",
    "chytomo.com": "A", "www.chytomo.com": "A",
    "bukvoid.com.ua": "A",
    "photo-lviv.in.ua": "A",
    "duh-i-litera.com": "A",
    "panic.com.ua": "A", "www.panic.com.ua": "A",
    "artac.org": "A", "www.artac.org": "A",
    "cyrillic.org.ua": "A", "www.cyrillic.org.ua": "A",
    "religion.in.ua": "A",
    "pravda.com.ua": "A",
    "ukrinform.ua": "A",
    "hromadske.ua": "A",
    "suspilne.media": "A",
    # B — RU-language media
    "pravmir.ru": "B", "www.pravmir.ru": "B",
    "blagovest-info.ru": "B", "www.blagovest-info.ru": "B",
    "artos.org": "B", "artos.gallery": "B",
    "calligraphy-museum.com": "B", "www.calligraphy-museum.com": "B",
    "radiovera.ru": "B",
    "museum.ru": "B", "www.museum.ru": "B",
    "gildehram.ru": "B",
    "tihvin-hram.ru": "B",
    "nsad.ru": "B", "www.nsad.ru": "B",
    "e-vestnik.ru": "B",
    "calligraphy-expo.com": "B",
    "calligraphy.mvk.ru": "B", "world.calligraphy-mvk.ru": "B",
    "incrussia.ru": "B",
    "praguedesignschool.com": "B", "www.praguedesignschool.com": "B",
    "ardexpert.ru": "B",
    "tovrest.ru": "B", "www.tovrest.ru": "B",
    "mitropolia.spb.ru": "B",
    "jmp.ru": "B", "www.jmp.ru": "B",
    "patriarchia.ru": "B", "www.patriarchia.ru": "B",
    "hramozdatel.ru": "B", "www.hramozdatel.ru": "B",
    "rublev.com": "B",
    "vestnikrhd.com": "B",
    "rp-net.ru": "B", "www.rp-net.ru": "B",
    "typomania.net": "B", "ru.typomania.net": "B",
    "pstgu.ru": "B", "www.pstgu.ru": "B",
    "nskmi.ru": "B", "www.nskmi.ru": "B",
    "calligraphy.com.ua": "B",  # Ukrainian calligraphy hub (RU-language)
    "tayga.info": "B",          # Russian regional news (Novosibirsk)
    "goldenbee.org": "B",       # Moscow design biennial (2016.goldenbee.org etc.)
    # C — International (IT/DE/Western)
    "russiacristiana.org": "C", "www.russiacristiana.org": "C",
    "meetingrimini.org": "C", "www.meetingrimini.org": "C",
    "scuolaseriate.eu": "C",
    "registroaziende.it": "C",
    "artrenewal.org": "C", "www.artrenewal.org": "C",
    "issuu.com": "C",
    "esxatos.com": "C",
    "clonline.org": "C", "www.clonline.org": "C",   # Comunione e Liberazione (IT)
    "progettoculturale.it": "C", "www.progettoculturale.it": "C",
    "centriculturali.org": "C",
    "arezzonotizie.it": "C", "www.arezzonotizie.it": "C",
    # E — Academic / DOI / PDF
    "hudprom.org.ua": "E",
    "visnik.org.ua": "E",
    "doi.org": "E",
    "monograph.com.ua": "E",
    "evnuir.vnu.edu.ua": "E",
    "search.worldcat.org": "E",
    "cius-archives.ca": "E",
    # F — Social media
    "youtube.com": "F", "www.youtube.com": "F",
    "facebook.com": "F", "www.facebook.com": "F",
    "instagram.com": "F", "www.instagram.com": "F",
    "vimeo.com": "F", "www.vimeo.com": "F",
    "flickr.com": "F", "www.flickr.com": "F",
    "t.me": "F", "telegram.me": "F",
    # A additions — UA domains missing from initial pass
    "gazeta.ua": "A",
    "artukraine.com.ua": "A",
    "kh.vgorode.ua": "A",
    "prostirliter.com": "A", "www.prostirliter.com": "A",
    "kyivcity.gov.ua": "A", "dsk-2023.kyivcity.gov.ua": "A",
    "artiya.com.ua": "A", "shop.artiya.com.ua": "A",
}

# Class weights for weighted recall
CLASS_WEIGHTS = {"A": 1.0, "B": 0.8, "C": 0.5, "D": 0.6, "E": 0.4, "F": 0.3, "G": 0.2}
CLASS_LABELS = {
    "A": "UA/EN web",
    "B": "RU-language media",
    "C": "International (IT/other)",
    "D": "Archive-only",
    "E": "Academic/DOI",
    "F": "Social media",
    "G": "Semantic",
}

# Archive domains — URL is "archive-only" if the original is dead
ARCHIVE_DOMAINS = {"web.archive.org", "archive.today", "archive.is", "archive.ph"}
SKIP_DOMAINS = {
    "uk.wikipedia.org", "en.wikipedia.org", "wikipedia.org",
    "web.archive.org", "archive.today", "archive.is", "archive.ph",
}

_MD_LINK_RE = re.compile(r'\(https?://[^)]+\)')


def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _resolve_domain_class(d: str) -> str | None:
    """Return class for domain d, walking up subdomain chain until match or None."""
    if d in DOMAIN_CLASS:
        return DOMAIN_CLASS[d]
    parts = d.split(".")
    for i in range(1, len(parts) - 1):
        parent = ".".join(parts[i:])
        if parent in DOMAIN_CLASS:
            return DOMAIN_CLASS[parent]
    return None


def _normalise_url(url: str) -> str:
    """Strip trailing slash and fragment for comparison."""
    url = url.rstrip("/").split("#")[0]
    return url


def parse_footnotes(md_path: Path) -> list[dict]:
    """
    Parse 167-footnotes MD file.
    Returns list of {ref, primary_urls, class, archive_only}.
    """
    entries = []
    text = md_path.read_text(encoding="utf-8", errors="replace")

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("|") and "Нумерація" in line:
            continue
        # Extract all (https?://...) from the line
        raw_urls = [m.group(0)[1:-1] for m in _MD_LINK_RE.finditer(line)]
        if not raw_urls:
            continue

        primary: list[str] = []
        archive: list[str] = []
        for u in raw_urls:
            d = _extract_domain(u)
            if d in SKIP_DOMAINS or not d:
                if d in ARCHIVE_DOMAINS:
                    archive.append(u)
                continue
            # skip worldcat ISSN-only
            if "worldcat.org/issn/" in u:
                continue
            primary.append(u)

        # If no primary but has archive → archive-only
        if not primary and archive:
            entries.append({"primary_urls": archive[:1], "class": "D", "archive_only": True})
        elif primary:
            # Classify by first primary URL
            cls = "G"  # default: semantic
            for u in primary:
                d = _extract_domain(u)
                resolved = _resolve_domain_class(d)
                if resolved:
                    cls = resolved
                    break
                # Fallback: check TLD
                if d.endswith(".ru") or d.endswith(".ru:80"):
                    cls = "B"
                    break
            entries.append({"primary_urls": primary, "class": cls, "archive_only": False})

    return entries


def load_pipeline_urls(db_path: Path) -> list[str]:
    """Load all source URLs from pipeline SQLite."""
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT url FROM sources WHERE url IS NOT NULL").fetchall()
    conn.close()
    return [r[0] for r in rows]


def find_db(run_arg: str | None) -> Path | None:
    if run_arg:
        p = Path(run_arg)
        if p.suffix == ".zip":
            return _extract_db_from_zip(p)
        if p.suffix in (".sqlite", ".db"):
            return p
        return None

    # Auto-discover latest output zip
    output_dir = Path("output")
    if not output_dir.exists():
        return None
    zips = sorted(output_dir.glob("*.zip"), reverse=True)
    if zips:
        return _extract_db_from_zip(zips[0])
    return None


def _extract_db_from_zip(zip_path: Path) -> Path | None:
    import tempfile
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        db_names = [n for n in names if n.endswith(".sqlite") or n.endswith(".db")]
        if not db_names:
            return None
        tmp = Path(tempfile.mkdtemp()) / "records.sqlite"
        with zf.open(db_names[0]) as src, open(tmp, "wb") as dst:
            dst.write(src.read())
    return tmp


def _domain_of(url: str) -> str:
    return _extract_domain(url)


_ARCHIVE_WRAP_RE = re.compile(
    r'https?://web\.archive\.org/web/\d+[a-z_]*/(?:https?:/)?/?(.*)',
    re.IGNORECASE,
)


def _unwrap_archive_url(url: str) -> str:
    """Extract original URL from web.archive.org wrapper."""
    m = _ARCHIVE_WRAP_RE.match(url)
    if m:
        orig = m.group(1)
        if not orig.startswith("http"):
            orig = "https://" + orig
        return orig
    return url


def run_benchmark(footnotes_path: Path, db_path: Path | None) -> None:
    gold = parse_footnotes(footnotes_path)

    # Build gold sets per class
    gold_by_class: dict[str, list[dict]] = {}
    for entry in gold:
        c = entry["class"]
        gold_by_class.setdefault(c, []).append(entry)

    total_gold = len(gold)
    print(f"\nGold standard: {total_gold} entries parsed from {footnotes_path.name}")

    for cls in sorted(gold_by_class):
        print(f"  Class {cls} ({CLASS_LABELS.get(cls, '?')}): {len(gold_by_class[cls])} entries")

    if db_path is None:
        print("\n[!] No pipeline DB found. Pass path to run .zip or .sqlite as first arg.")
        print("    Only gold distribution shown above.")
        return

    pipeline_urls = load_pipeline_urls(db_path)
    print(f"\nPipeline sources loaded: {len(pipeline_urls)} URLs from {db_path.name}")

    # Build lookup structures
    pipeline_url_set = {_normalise_url(u) for u in pipeline_urls}
    pipeline_domain_set = {_domain_of(u) for u in pipeline_urls}

    # Score per class
    print("\n" + "=" * 72)
    print(f"{'Class':<4} {'Label':<26} {'Gold':>5} {'L1 exact':>9} {'L2 domain':>10} {'Score':>7}")
    print("-" * 72)

    class_scores: dict[str, float] = {}
    class_gold_n: dict[str, int] = {}

    for cls in ["A", "B", "C", "D", "E", "F", "G"]:
        entries = gold_by_class.get(cls, [])
        n = len(entries)
        class_gold_n[cls] = n
        if n == 0:
            class_scores[cls] = 0.0
            continue

        l1 = l2 = 0
        for entry in entries:
            # For Class D: unwrap the archive URL to get original domain
            check_urls = entry["primary_urls"]
            if cls == "D":
                check_urls = [_unwrap_archive_url(u) for u in check_urls if _unwrap_archive_url(u)]

            for u in check_urls:
                norm = _normalise_url(u)
                if norm in pipeline_url_set:
                    l1 += 1
                    break
            else:
                for u in check_urls:
                    d = _domain_of(u)
                    if d and d not in ARCHIVE_DOMAINS and d in pipeline_domain_set:
                        l2 += 1
                        break

        # score = (L1*1.0 + L2*0.5) / n
        score = (l1 * 1.0 + l2 * 0.5) / n
        class_scores[cls] = score
        label = CLASS_LABELS.get(cls, "?")
        print(f"  {cls}   {label:<26} {n:>5} {l1:>9} {l2:>10} {score:>7.1%}")

    print("=" * 72)

    # Weighted recall
    w_total = sum(CLASS_WEIGHTS[c] * class_gold_n[c] for c in class_scores if class_gold_n[c] > 0)
    w_recall = sum(CLASS_WEIGHTS[c] * class_scores[c] * class_gold_n[c]
                   for c in class_scores if class_gold_n[c] > 0) / (w_total or 1)
    print(f"\nWeighted recall: {w_recall:.1%}  (weights A=1.0 B=0.8 C=0.5 D=0.6 E=0.4 F=0.3 G=0.2)")

    # Missing class B sample
    print("\nClass B — missed domains (sample):")
    missed_b_domains: dict[str, int] = {}
    for entry in gold_by_class.get("B", []):
        for u in entry["primary_urls"]:
            d = _domain_of(u)
            if d not in pipeline_domain_set:
                missed_b_domains[d] = missed_b_domains.get(d, 0) + 1
    for d, n in sorted(missed_b_domains.items(), key=lambda x: -x[1])[:10]:
        print(f"  {d}: {n} refs")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python benchmark_gold_standard.py [run.zip|records.sqlite] footnotes.md")
        print("  footnotes.md — file with 167 Wikipedia source footnotes for Чекаль")
        sys.exit(1)

    fn_path = Path(sys.argv[2])
    run_arg = sys.argv[1] if len(sys.argv) > 1 else None

    if not fn_path.exists():
        print(f"Footnotes file not found: {fn_path}")
        print("Pass path as second argument: python benchmark_gold_standard.py [run.zip] footnotes.md")
        sys.exit(1)

    db = find_db(run_arg)
    run_benchmark(fn_path, db)
