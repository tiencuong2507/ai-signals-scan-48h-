import time
from datetime import datetime, timezone, timedelta

import storage
import analyzer
import analyzer_deep
import reporter
from collectors.rss_collector import fetch_all
from collectors.github_trending import fetch_trending
from config import MAX_ARTICLES_PER_RUN, MAX_ARTICLES_DEEP, RELEVANT_KEYWORDS, SCAN_MODE, GH_DISPATCH_TOKEN


def _keyword_match(article: dict) -> bool:
    """Pre-filter nhanh bằng keyword trước khi gọi Gemini."""
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()
    return any(kw.lower() in text for kw in RELEVANT_KEYWORDS)


def run():
    tz_hcm = timezone(timedelta(hours=7))
    run_time = datetime.now(tz_hcm)
    print(f"\n{'='*55}")
    print(f"  AI SIGNALS SCAN — {run_time.strftime('%Y-%m-%d %H:%M UTC+7')}")
    print(f"{'='*55}\n")

    is_deep = SCAN_MODE == "deep"
    cap = MAX_ARTICLES_DEEP if is_deep else MAX_ARTICLES_PER_RUN
    mode_label = "🔬 DEEP (Claude Sonnet)" if is_deep else "⚡ FAST (Gemini Flash)"
    print(f"  Mode: {mode_label}\n")

    storage.init_db()

    # 1. Fetch all sources
    print("── [1/5] Fetching sources...")
    raw_articles = fetch_all()
    github_repos = fetch_trending(days_back=7, top_n=20)
    raw_articles = raw_articles + github_repos
    print(f"     → {len(raw_articles)} total items fetched\n")

    # 2. Deduplicate (deep mode bỏ qua — luôn phân tích lại bài mới nhất)
    print("── [2/5] Deduplicating...")
    if is_deep:
        new_articles = raw_articles
        print(f"     → Deep mode: bỏ qua dedup, phân tích lại {len(new_articles)} bài\n")
    else:
        new_articles = [a for a in raw_articles if not storage.is_seen(a["url"])]
        print(f"     → {len(new_articles)} new (skipped {len(raw_articles) - len(new_articles)} seen)\n")

    if not new_articles:
        print("  ✓ No new articles. Newsletter not updated.")
        return

    # 3. Sort by recency (newest first) + keyword pre-filter
    print("── [3/5] Sorting & pre-filtering...")
    new_articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)
    pre_filtered = [a for a in new_articles if _keyword_match(a)]
    skipped_kw = len(new_articles) - len(pre_filtered)
    print(f"     → {len(pre_filtered)} passed keyword filter (dropped {skipped_kw} irrelevant)\n")

    candidates = pre_filtered[:cap]
    if len(pre_filtered) > cap:
        print(f"     → Capping to {cap} most recent\n")

    # 4. Analyze
    engine_label = "Claude Sonnet (deep)" if is_deep else "Gemini Flash (fast)"
    print(f"── [4/5] Analyzing {len(candidates)} items with {engine_label}...")
    analyze_fn = analyzer_deep.analyze if is_deep else analyzer.analyze
    analyzed = []
    for i, article in enumerate(candidates, 1):
        result = analyze_fn(article)
        storage.save({**article, **(result or {})})
        if result:
            analyzed.append(result)
            impact = result.get("impact_score", "-")
            status = f"✓  [{result.get('domain','?'):14}] impact={impact} {article['title'][:45]}"
        else:
            status = f"✗  (skip) {article['title'][:60]}"
        print(f"  {i:3}/{len(candidates)}  {status}")
        time.sleep(0.2)

    print(f"\n     → {len(analyzed)} relevant items kept\n")

    if not analyzed:
        print("  ✓ No relevant articles found. Newsletter not updated.")
        return

    # 5. Generate newsletter (sorted by impact inside reporter)
    print("── [5/5] Generating newsletter...")
    reporter.generate(analyzed, run_time, gh_token=GH_DISPATCH_TOKEN)

    print(f"\n{'='*55}")
    print(f"  ✓ Done! {len(analyzed)} signals in this edition.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    run()
