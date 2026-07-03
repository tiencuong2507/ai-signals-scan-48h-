import feedparser
from datetime import datetime, timezone
from config import RSS_SOURCES, HOURS_BACK


def fetch_all(hours_back: int = HOURS_BACK) -> list[dict]:
    articles = []
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries:
                pub = _parse_date(entry)
                if pub is None or not _is_recent(pub, hours_back):
                    continue
                url = entry.get("link", "").strip()
                title = entry.get("title", "").strip()
                if not url or not title:
                    continue
                summary = _clean_html(entry.get("summary", "") or entry.get("description", ""))
                articles.append({
                    "url": url,
                    "title": title,
                    "summary": summary[:1200],
                    "source": source["name"],
                    "source_domain": source["domain"],
                    "published_at": pub.isoformat(),
                })
            print(f"[OK] {source['name']}: {len(feed.entries)} entries")
        except Exception as e:
            print(f"[WARN] {source['name']}: {e}")
    return articles


def _parse_date(entry) -> datetime | None:
    import time
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                continue
    return None


def _is_recent(pub: datetime, hours: int) -> bool:
    delta = datetime.now(timezone.utc) - pub
    return delta.total_seconds() <= hours * 3600


def _clean_html(text: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
