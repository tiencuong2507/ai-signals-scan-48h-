"""Thu thập bài từ các subreddit kỹ thuật liên quan."""
import feedparser
import time
import re
from datetime import datetime, timezone

SUBREDDITS = [
    # AI & Công nghệ
    ("MachineLearning",   "ai_tech"),
    ("artificial",        "ai_tech"),
    ("singularity",       "ai_tech"),
    ("robotics",          "ai_tech"),
    ("automation",        "ai_tech"),
    # Xây dựng
    ("construction",      "construction"),
    ("BuildingAutomation","construction"),
    ("ArchitectureDesign","construction"),
    # Sản xuất
    ("manufacturing",     "manufacturing"),
    ("IndustrialEngineering", "manufacturing"),
    # Cơ điện lạnh
    ("HVAC",              "hvac_mep"),
    ("HeatPumps",         "hvac_mep"),
    ("energyefficiency",  "hvac_mep"),
]

BASE_URL = "https://www.reddit.com/r/{sub}/new.rss"
HEADERS = {"User-Agent": "AISignalBot/1.0 (research aggregator)"}


def fetch_reddit(max_per_sub: int = 8) -> list[dict]:
    import requests

    articles = []
    seen_urls = set()

    for sub, domain in SUBREDDITS:
        try:
            resp = requests.get(
                BASE_URL.format(sub=sub),
                headers=HEADERS,
                timeout=10,
            )
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:max_per_sub]:
                link = entry.get("link", "")
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                published = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()

                summary = entry.get("summary", "")
                summary = re.sub(r"<[^>]+>", " ", summary).strip()[:500]

                articles.append({
                    "url": link,
                    "title": entry.get("title", "").strip(),
                    "source": f"Reddit r/{sub}",
                    "summary": summary,
                    "published_at": published,
                    "domain": domain,
                })
            time.sleep(0.5)
        except Exception as e:
            print(f"[WARN] Reddit r/{sub} failed — {e}")
            continue

    print(f"  [Reddit] {len(articles)} posts fetched")
    return articles
