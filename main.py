import sys
import time
from datetime import datetime, timezone

import storage
import analyzer
import reporter
from collectors.rss_collector import fetch_all
from config import MAX_ARTICLES_PER_RUN


def run():
    run_time = datetime.now(timezone.utc)
    print(f"\n{'='*55}")
    print(f"  AI SIGNALS SCAN 48H — {run_time.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*55}\n")

    # 1. Init DB
    storage.init_db()

    # 2. Fetch RSS
    print("── [1/4] Fetching RSS feeds...")
    raw_articles = fetch_all()
    print(f"     → {len(raw_articles)} articles fetched\n")

    # 3. Deduplicate against DB
    print("── [2/4] Deduplicating...")
    new_articles = [a for a in raw_articles if not storage.is_seen(a["url"])]
    print(f"     → {len(new_articles)} new (skipped {len(raw_articles) - len(new_articles)} seen)\n")

    if not new_articles:
        print("  ✓ No new articles. Newsletter not updated.")
        return

    # Cap to limit cost
    if len(new_articles) > MAX_ARTICLES_PER_RUN:
        print(f"     → Capping to {MAX_ARTICLES_PER_RUN} articles\n")
        new_articles = new_articles[:MAX_ARTICLES_PER_RUN]

    # 4. Analyze with Claude
    print(f"── [3/4] Analyzing {len(new_articles)} articles with Claude...")
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
        time.sleep(0.3)  # Gentle rate limit

    print(f"\n     → {len(analyzed)} relevant articles kept\n")

    if not analyzed:
        print("  ✓ No relevant articles found. Newsletter not updated.")
        return

    # 5. Generate newsletter
    print("── [4/4] Generating newsletter...")
    reporter.generate(analyzed, run_time)

    print(f"\n{'='*55}")
    print(f"  ✓ Done! {len(analyzed)} signals in this edition.")
    print(f"  → docs/index.html")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    run()
