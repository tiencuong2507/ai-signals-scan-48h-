import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/signals.db")


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                url              TEXT PRIMARY KEY,
                title            TEXT,
                source           TEXT,
                source_domain    TEXT,
                published_at     TEXT,
                scanned_at       TEXT,
                domain           TEXT,
                category         TEXT,
                tags             TEXT,
                reliability      INTEGER,
                depth            TEXT,
                practicality     TEXT,
                summary_vi       TEXT
            )
        """)


def is_seen(url: str) -> bool:
    with _conn() as conn:
        row = conn.execute("SELECT 1 FROM articles WHERE url = ?", (url,)).fetchone()
    return row is not None


def save(article: dict):
    with _conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO articles VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            article["url"],
            article["title"],
            article["source"],
            article.get("source_domain", article.get("domain", "")),
            article.get("published_at", ""),
            datetime.utcnow().isoformat(),
            article.get("domain", ""),
            article.get("category", ""),
            json.dumps(article.get("tags", []), ensure_ascii=False),
            article.get("reliability_score", 0),
            article.get("depth", ""),
            article.get("practicality", ""),
            article.get("summary_vi", ""),
        ))


def _conn():
    return sqlite3.connect(DB_PATH)
