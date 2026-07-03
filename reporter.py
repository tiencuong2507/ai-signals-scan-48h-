from datetime import datetime
from pathlib import Path
from config import DOMAIN_LABELS, DEPTH_LABELS, PRACTICALITY_LABELS

DOCS_DIR = Path("docs")
ARCHIVE_DIR = DOCS_DIR / "archive"


def generate(articles: list[dict], run_time: datetime):
    DOCS_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)

    html = _build_html(articles, run_time)

    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    dated = run_time.strftime("%Y-%m-%d_%H-%M")
    (ARCHIVE_DIR / f"{dated}.html").write_text(html, encoding="utf-8")
    _update_archive_index()

    print(f"[OK] Newsletter saved → docs/index.html ({len(articles)} articles)")


def _build_html(articles: list[dict], run_time: datetime) -> str:
    grouped: dict[str, list] = {}
    for a in articles:
        d = a.get("domain", "ai_tech")
        grouped.setdefault(d, []).append(a)

    domain_order = ["construction", "manufacturing", "hvac_mep", "ai_tech"]
    sections_html = ""
    for domain in domain_order:
        items = grouped.get(domain, [])
        if not items:
            continue
        items.sort(key=lambda x: x.get("reliability_score", 0), reverse=True)
        sections_html += _section(domain, items)

    date_str = run_time.strftime("%d/%m/%Y %H:%M UTC")
    total = len(articles)

    counts = {d: len(grouped.get(d, [])) for d in domain_order}
    stat_badges = "".join(
        f'<span class="stat-badge">{DOMAIN_LABELS.get(d, d)}: <b>{counts[d]}</b></span>'
        for d in domain_order if counts[d]
    )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Signals Scan 48H — {run_time.strftime('%d/%m/%Y')}</title>
<style>
  :root {{
    --bg: #0f1117; --surface: #1a1d27; --surface2: #222637;
    --border: #2d3148; --accent: #60a5fa; --green: #34d399;
    --orange: #fb923c; --purple: #a78bfa; --yellow: #fbbf24;
    --text: #e2e8f0; --muted: #64748b; --red: #f87171;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif;
         font-size: 14px; line-height: 1.6; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  /* HEADER */
  .header {{ background: linear-gradient(135deg, #0f1b3d 0%, #1a0f2e 100%);
             border-bottom: 1px solid var(--border); padding: 28px 24px 20px; }}
  .header h1 {{ font-size: 22px; font-weight: 800; color: #fff; letter-spacing: 1px; }}
  .header h1 span {{ color: var(--accent); }}
  .header .meta {{ font-size: 11px; color: var(--muted); margin-top: 6px; }}
  .stat-badges {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
  .stat-badge {{ background: var(--surface2); border: 1px solid var(--border);
                 border-radius: 20px; padding: 3px 10px; font-size: 11px; color: var(--muted); }}
  .stat-badge b {{ color: var(--text); }}
  .total-badge {{ background: #1e3a5f; border-color: #2563eb;
                  color: var(--accent); font-weight: 700; }}

  /* LAYOUT */
  .container {{ max-width: 960px; margin: 0 auto; padding: 20px 16px 60px; }}

  /* SECTION */
  .section {{ margin-bottom: 32px; }}
  .section-title {{ font-size: 15px; font-weight: 700; padding: 10px 14px;
                    border-radius: 8px 8px 0 0; border: 1px solid var(--border);
                    border-bottom: none; letter-spacing: 0.5px; }}
  .section-construction .section-title {{ background: #0f1f1a; color: #34d399; border-color: #065f46; }}
  .section-manufacturing .section-title {{ background: #1a0f0f; color: #fb923c; border-color: #7c2d12; }}
  .section-hvac_mep .section-title     {{ background: #0f1a2e; color: #60a5fa; border-color: #1e3a5f; }}
  .section-ai_tech .section-title      {{ background: #1a0f2e; color: #a78bfa; border-color: #4c1d95; }}

  /* CARD */
  .card {{ background: var(--surface); border: 1px solid var(--border);
           border-top: none; padding: 16px 18px; transition: background .15s; }}
  .card:last-child {{ border-radius: 0 0 8px 8px; }}
  .card:not(:last-child) {{ border-bottom-color: var(--surface2); }}
  .card:hover {{ background: var(--surface2); }}

  .card-header {{ display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px; }}
  .card-title {{ font-size: 14px; font-weight: 600; color: var(--text); flex: 1; line-height: 1.4; }}
  .card-source {{ font-size: 10px; color: var(--muted); margin-top: 2px; }}

  /* BADGES */
  .badges {{ display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }}
  .badge {{ border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 600;
            border: 1px solid; }}
  .badge-category {{ background: #1e293b; border-color: #334155; color: #94a3b8; }}
  .badge-reliability {{ color: #fff; }}
  .rel-high  {{ background: #14532d; border-color: #16a34a; }}
  .rel-mid   {{ background: #713f12; border-color: #d97706; }}
  .rel-low   {{ background: #450a0a; border-color: #dc2626; }}
  .badge-depth {{ background: #1e1b4b; border-color: #4338ca; color: #a5b4fc; }}
  .badge-prac  {{ background: #064e3b; border-color: #059669; color: #6ee7b7; }}
  .badge-prac-future {{ background: #1c1917; border-color: #78716c; color: #a8a29e; }}
  .badge-prac-research {{ background: #1f1035; border-color: #7c3aed; color: #c4b5fd; }}

  /* SUMMARY */
  .summary {{ font-size: 12.5px; color: #94a3b8; line-height: 1.7;
              border-left: 3px solid var(--border); padding-left: 12px; }}
  .summary p {{ margin: 2px 0; }}

  /* TAGS */
  .tags {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 10px; }}
  .tag {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 3px;
          padding: 1px 6px; font-size: 10px; color: var(--muted); }}

  /* FOOTER */
  .footer {{ text-align: center; padding: 20px; font-size: 11px; color: var(--muted);
             border-top: 1px solid var(--border); margin-top: 20px; }}
  .footer a {{ color: var(--muted); }}

  /* ARCHIVE LINK */
  .archive-link {{ text-align: right; font-size: 11px; color: var(--muted);
                   padding: 8px 0 0; }}
</style>
</head>
<body>

<div class="header">
  <h1>⚡ AI SIGNALS <span>SCAN</span> 48H</h1>
  <div class="meta">Quét tự động lúc {date_str} &nbsp;·&nbsp; Xây dựng · Sản xuất · Cơ điện lạnh</div>
  <div class="stat-badges">
    <span class="stat-badge total-badge">Tổng: <b>{total} tín hiệu</b></span>
    {stat_badges}
  </div>
</div>

<div class="container">
  <div class="archive-link"><a href="archive/">📁 Xem bản tin cũ</a></div>
  {sections_html}
</div>

<div class="footer">
  Tạo bởi AI Signals Scan 48H &nbsp;·&nbsp; Powered by Claude API
  &nbsp;·&nbsp; <a href="archive/">Kho lưu trữ</a>
</div>

</body>
</html>"""


def _section(domain: str, items: list) -> str:
    label = DOMAIN_LABELS.get(domain, domain)
    cards = "".join(_card(a) for a in items)
    return f"""
<div class="section section-{domain}">
  <div class="section-title">{label} &nbsp;·&nbsp; {len(items)} bài</div>
  {cards}
</div>"""


def _card(a: dict) -> str:
    title = a.get("title", "")
    url = a.get("url", "#")
    source = a.get("source", "")
    pub = a.get("published_at", "")[:10]
    category = a.get("category", "")
    tags = a.get("tags", [])
    rel = a.get("reliability_score", 0)
    depth = a.get("depth", "")
    prac = a.get("practicality", "")
    summary_vi = a.get("summary_vi", "")

    rel_class = "rel-high" if rel >= 7 else ("rel-mid" if rel >= 5 else "rel-low")
    rel_label = f"★ {rel}/10"

    depth_label = DEPTH_LABELS.get(depth, depth)
    prac_label = PRACTICALITY_LABELS.get(prac, prac)
    prac_class = {"now": "badge-prac", "near_future": "badge-prac-future", "research": "badge-prac-research"}.get(prac, "badge-prac")

    summary_html = ""
    if summary_vi:
        lines = [l.strip() for l in summary_vi.split("\n") if l.strip()]
        summary_html = '<div class="summary">' + "".join(f"<p>{l}</p>" for l in lines) + "</div>"

    tags_html = ""
    if tags:
        tags_html = '<div class="tags">' + "".join(f'<span class="tag">{t}</span>' for t in tags) + "</div>"

    return f"""
<div class="card">
  <div class="card-header">
    <div>
      <div class="card-title"><a href="{url}" target="_blank">{title}</a></div>
      <div class="card-source">{source} &nbsp;·&nbsp; {pub}</div>
    </div>
  </div>
  <div class="badges">
    <span class="badge badge-category">{category}</span>
    <span class="badge badge-reliability {rel_class}">{rel_label}</span>
    <span class="badge badge-depth">{depth_label}</span>
    <span class="badge {prac_class}">{prac_label}</span>
  </div>
  {summary_html}
  {tags_html}
</div>"""


def _update_archive_index():
    files = sorted(ARCHIVE_DIR.glob("*.html"), reverse=True)
    items = ""
    for f in files:
        name = f.stem.replace("_", " ")
        items += f'<li><a href="{f.name}">{name}</a></li>\n'

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"><title>Kho lưu trữ — AI Signals 48H</title>
<style>
  body {{ background:#0f1117; color:#e2e8f0; font-family:'Segoe UI',sans-serif;
         max-width:600px; margin:40px auto; padding:0 16px; }}
  h1 {{ color:#60a5fa; margin-bottom:20px; }}
  ul {{ list-style:none; }}
  li {{ padding:8px 0; border-bottom:1px solid #1e293b; }}
  a {{ color:#93c5fd; text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .back {{ font-size:12px; margin-bottom:16px; }}
</style>
</head>
<body>
<div class="back"><a href="../index.html">← Bản tin mới nhất</a></div>
<h1>📁 Kho lưu trữ</h1>
<ul>{items}</ul>
</body>
</html>"""
    (ARCHIVE_DIR / "index.html").write_text(html, encoding="utf-8")
