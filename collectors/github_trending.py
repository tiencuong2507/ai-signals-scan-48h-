import requests
from datetime import datetime, timezone, timedelta


TOPICS = [
    "artificial-intelligence", "machine-learning", "computer-vision",
    "robotics", "automation", "building-information-modeling",
    "digital-twin", "iot", "energy-efficiency", "manufacturing",
]

HEADERS = {"Accept": "application/vnd.github+json"}


def fetch_trending(days_back: int = 7, top_n: int = 20) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    query = f"created:>{since} stars:>10"
    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": top_n}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception as e:
        print(f"[WARN] GitHub Trending: {e}")
        return []

    articles = []
    for repo in items:
        description = repo.get("description") or ""
        topics_list = repo.get("topics", [])
        stars = repo.get("stargazers_count", 0)
        lang = repo.get("language") or "N/A"
        created = repo.get("created_at", "")[:10]

        summary = (
            f"{description}. "
            f"Stars tuần này: ⭐{stars:,}. "
            f"Ngôn ngữ: {lang}. "
            f"Topics: {', '.join(topics_list[:6]) or 'N/A'}."
        )

        articles.append({
            "url": repo.get("html_url", ""),
            "title": f"[GitHub ⭐{stars:,}] {repo.get('full_name', '')}",
            "summary": summary[:1200],
            "source": "GitHub Trending",
            "source_domain": "ai_tech",
            "published_at": created,
        })

    print(f"[OK] GitHub Trending: {len(articles)} repos")
    return articles
