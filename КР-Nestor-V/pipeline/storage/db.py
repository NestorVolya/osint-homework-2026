import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone


class Database:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()
        self._migrate_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id   TEXT PRIMARY KEY,
                actor_id    TEXT NOT NULL,
                date_raw    TEXT,
                location_raw TEXT,
                source_type TEXT,
                url         TEXT UNIQUE,
                title       TEXT,
                text        TEXT,
                content_hash TEXT,
                collected_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS locations (
                location_id TEXT PRIMARY KEY,
                city        TEXT,
                country     TEXT,
                raw         TEXT
            );

            CREATE TABLE IF NOT EXISTS events (
                event_id    TEXT PRIMARY KEY,
                actor_id    TEXT NOT NULL,
                date        TEXT,
                war_context TEXT,
                location_id TEXT,
                title       TEXT,
                description TEXT,
                source_id   TEXT,
                FOREIGN KEY (location_id) REFERENCES locations(location_id),
                FOREIGN KEY (source_id)   REFERENCES sources(source_id)
            );

            CREATE TABLE IF NOT EXISTS statements (
                statement_id  TEXT PRIMARY KEY,
                actor_id      TEXT NOT NULL,
                date          TEXT,
                war_context   TEXT,
                platform      TEXT,
                quote         TEXT,
                summary       TEXT,
                rhetoric_type TEXT,
                source_id     TEXT,
                FOREIGN KEY (source_id) REFERENCES sources(source_id)
            );

            CREATE TABLE IF NOT EXISTS links (
                link_id    TEXT PRIMARY KEY,
                subject_a  TEXT NOT NULL,
                subject_b  TEXT NOT NULL,
                link_type  TEXT,
                period     TEXT,
                context    TEXT,
                flags      TEXT,
                source_id  TEXT,
                FOREIGN KEY (source_id) REFERENCES sources(source_id)
            );

            CREATE TABLE IF NOT EXISTS accounts (
                account_id   TEXT PRIMARY KEY,
                platform     TEXT NOT NULL,
                handle       TEXT,
                url          TEXT UNIQUE,
                display_name TEXT,
                bio          TEXT,
                first_seen   TEXT,
                last_seen    TEXT,
                sources_json TEXT
            );

            CREATE TABLE IF NOT EXISTS geoclusters (
                cluster_id  TEXT PRIMARY KEY,
                type        TEXT,
                period      TEXT,
                location_id TEXT,
                count       INTEGER,
                FOREIGN KEY (location_id) REFERENCES locations(location_id)
            );
        """)
        self.conn.commit()

    def _migrate_schema(self):
        cols = {row[1] for row in self.conn.execute("PRAGMA table_info(links)")}
        if "evidence_quote" not in cols:
            self.conn.execute("ALTER TABLE links ADD COLUMN evidence_quote TEXT")
            self.conn.commit()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # --- sources ---

    def insert_source(self, source_id: str, actor_id: str, url: str, title: str,
                      text: str, source_type: str = None, date_raw: str = None,
                      location_raw: str = None, content_hash: str = None):
        self.conn.execute(
            """INSERT OR IGNORE INTO sources
               (source_id, actor_id, date_raw, location_raw, source_type,
                url, title, text, content_hash, collected_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (source_id, actor_id, date_raw, location_raw, source_type,
             url, title, text, content_hash, self._now()),
        )
        self.conn.commit()

    def get_sources(self, actor_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM sources WHERE actor_id = ?", (actor_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # --- locations ---

    def upsert_location(self, location_id: str, city: str, country: str, raw: str):
        self.conn.execute(
            """INSERT OR IGNORE INTO locations (location_id, city, country, raw)
               VALUES (?, ?, ?, ?)""",
            (location_id, city, country, raw),
        )
        self.conn.commit()

    # --- events ---

    def insert_event(self, event_id: str, actor_id: str, date: str, title: str,
                     description: str = None, war_context: str = None,
                     location_id: str = None, source_id: str = None):
        self.conn.execute(
            """INSERT OR IGNORE INTO events
               (event_id, actor_id, date, war_context, location_id,
                title, description, source_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_id, actor_id, date, war_context, location_id,
             title, description, source_id),
        )
        self.conn.commit()

    def get_events(self, actor_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM events WHERE actor_id = ? ORDER BY date", (actor_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_events_with_location(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM events WHERE location_id IS NOT NULL ORDER BY date"
        ).fetchall()
        return [dict(r) for r in rows]

    # --- statements ---

    def insert_statement(self, statement_id: str, actor_id: str, quote: str,
                         summary: str = None, date: str = None, platform: str = None,
                         war_context: str = None, rhetoric_type: str = None,
                         source_id: str = None):
        self.conn.execute(
            """INSERT OR IGNORE INTO statements
               (statement_id, actor_id, date, war_context, platform,
                quote, summary, rhetoric_type, source_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (statement_id, actor_id, date, war_context, platform,
             quote, summary, rhetoric_type, source_id),
        )
        self.conn.commit()

    def get_statements(self, actor_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM statements WHERE actor_id = ? ORDER BY date", (actor_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # --- links ---

    def insert_link(self, link_id: str, subject_a: str, subject_b: str,
                    link_type: str = None, period: str = None, context: str = None,
                    flags: list = None, source_id: str = None,
                    evidence_quote: str = None):
        self.conn.execute(
            """INSERT OR IGNORE INTO links
               (link_id, subject_a, subject_b, link_type, period, context, flags, source_id, evidence_quote)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (link_id, subject_a, subject_b, link_type, period, context,
             json.dumps(flags or [], ensure_ascii=False), source_id, evidence_quote),
        )
        self.conn.commit()

    def get_links(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM links").fetchall()
        return [dict(r) for r in rows]

    # --- accounts ---

    def upsert_account(self, account_id: str, platform: str, url: str = None,
                       handle: str = None, display_name: str = None, bio: str = None,
                       first_seen: str = None, last_seen: str = None,
                       sources: list = None):
        self.conn.execute(
            """INSERT OR IGNORE INTO accounts
               (account_id, platform, handle, url, display_name, bio,
                first_seen, last_seen, sources_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (account_id, platform, handle, url, display_name, bio,
             first_seen, last_seen, json.dumps(sources or [], ensure_ascii=False)),
        )
        self.conn.commit()

    def get_accounts(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM accounts").fetchall()
        return [dict(r) for r in rows]

    # --- geoclusters ---

    def insert_geocluster(self, cluster_id: str, type_: str, period: str,
                          location_id: str, count: int):
        self.conn.execute(
            """INSERT OR REPLACE INTO geoclusters
               (cluster_id, type, period, location_id, count)
               VALUES (?, ?, ?, ?, ?)""",
            (cluster_id, type_, period, location_id, count),
        )
        self.conn.commit()

    def get_geoclusters(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM geoclusters").fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.conn.close()
