"""Thu thập tin từ Google News RSS theo từ khóa chuyên ngành."""
import feedparser
import time
from datetime import datetime, timezone

# Các từ khóa tìm kiếm theo từng lĩnh vực
QUERIES = [
    # AI & Công nghệ ứng dụng
    "artificial intelligence manufacturing automation",
    "AI construction building technology",
    "machine learning industrial application",
    # Xây dựng
    "construction technology BIM innovation",
    "smart building automation digital twin",
    "prefab modular construction robot",
    # Sản xuất
    "Industry 4.0 factory automation AI",
    "manufacturing robot quality control",
    # Cơ điện lạnh / MEP
    "HVAC heat pump energy efficiency AI",
    "building energy management system",
    "MEP mechanical electrical construction",
    # Việt Nam
    "Vietnam construction technology",
    "Vietnam manufacturing automation",
]

BASE_URL = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def fetch_google_news(max_per_query: int = 8) -> list[dict]:
    articles = []
    seen_urls = set()

    for query in QUERIES:
        try:
            url = BASE_URL.format(q=query.replace(" ", "+"))
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_query]:
                link = entry.get("link", "")
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                published = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()

                summary = entry.get("summary", "")
                # Bỏ HTML tags đơn giản
                import re
                summary = re.sub(r"<[^>]+>", " ", summary).strip()

                articles.append({
                    "url": link,
                    "title": entry.get("title", "").strip(),
                    "source": f"Google News – {query[:30]}",
                    "summary": summary[:500],
                    "published_at": published,
                })
            time.sleep(0.3)
        except Exception as e:
            print(f"[WARN] Google News query failed: {query[:30]} — {e}")
            continue

    print(f"  [Google News] {len(articles)} articles fetched")
    return articles
