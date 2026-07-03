import time
from datetime import datetime, timezone

import storage
import analyzer
import reporter
from collectors.rss_collector import fetch_all
from collectors.github_trending import fetch_trending
from config import MAX_ARTICLES_PER_RUN


def run():
    run_time = datetime.now(timezone.utc)
    print(f"\n{'='*55}")
    print(f"  AI SIGNALS SCAN — {run_time.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*55}\n")

    storage.init_db()

    # 1. Fetch all sources
    print("── [1/4] Fetching sources...")
    raw_articles = fetch_all()
    github_repos = fetch_trending(days_back=7, top_n=20)
    raw_articles = raw_articles + github_repos
    print(f"     → {len(raw_articles)} total items fetched\n")

    # 2. Deduplicate
    print("── [2/4] Deduplicating...")
    new_articles = [a for a in raw_articles if not storage.is_seen(a["url"])]
    print(f"     → {len(new_articles)} new (skipped {len(raw_articles) - len(new_articles)} seen)\n")

    if not new_articles:
        print("  ✓ No new articles. Newsletter not updated.")
        return

    if len(new_articles) > MAX_ARTICLES_PER_RUN:
        print(f"     → Capping to {MAX_ARTICLES_PER_RUN} articles\n")
        new_articles = new_articles[:MAX_ARTICLES_PER_RUN]

    # 3. Analyze with Gemini
    print(f"── [3/4] Analyzing {len(new_articles)} items with Gemini...")
    analyzed = []
    for i, article in enumerate(new_articles, 1):
        result = analyzer.analyze(article)
        storage.save({**article, **(result or {})})
        if result:
            analyzed.append(result)
            status = f"✓  [{result.get('domain','?'):14}] {article['title'][:55]}"
        else:
            status = f"✗  (skip) {article['title'][:60]}"
        print(f"  {i:3}/{len(new_articles)}  {status}")
        time.sleep(0.2)

    print(f"\n     → {len(analyzed)} relevant items kept\n")

    if not analyzed:
        print("  ✓ No relevant articles found. Newsletter not updated.")
        return

    # 4. Generate newsletter
    print("── [4/4] Generating newsletter...")
    reporter.generate(analyzed, run_time)

    print(f"\n{'='*55}")
    print(f"  ✓ Done! {len(analyzed)} signals in this edition.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    run()
