import os
from datetime import datetime
from pathlib import Path
from config import DOMAIN_LABELS, DEPTH_LABELS, PRACTICALITY_LABELS

DOCS_DIR = Path("docs")
ARCHIVE_DIR = DOCS_DIR / "archive"

REPO = "tiencuong2507/ai-signals-scan-48h-"
ACTIONS_URL = f"https://github.com/{REPO}/actions/workflows/scan.yml"


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

    tab_buttons = f'<button class="tab active" data-domain="all">🔎 Tất cả <span class="tab-count">{total}</span></button>'
    for d in domain_order:
        if counts[d]:
            label = DOMAIN_LABELS.get(d, d)
            tab_buttons += f'<button class="tab" data-domain="{d}">{label} <span class="tab-count">{counts[d]}</span></button>'

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Signals Scan — {run_time.strftime('%d/%m/%Y')}</title>
<style>
  :root {{
    --bg:#0f1117; --surface:#1a1d27; --surface2:#222637;
    --border:#2d3148; --accent:#60a5fa; --text:#e2e8f0; --muted:#64748b;
  }}
  *{{ box-sizing:border-box; margin:0; padding:0; }}
  body{{ background:var(--bg); color:var(--text); font-family:'Segoe UI',system-ui,sans-serif;
        font-size:14px; line-height:1.6; }}
  a{{ color:var(--accent); text-decoration:none; }}
  a:hover{{ text-decoration:underline; }}

  /* HEADER */
  .header{{ background:linear-gradient(135deg,#0f1b3d 0%,#1a0f2e 100%);
            border-bottom:1px solid var(--border); padding:20px 24px 0; }}
  .header-top{{ display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:12px; }}
  .header h1{{ font-size:20px; font-weight:800; color:#fff; letter-spacing:1px; }}
  .header h1 span{{ color:var(--accent); }}
  .header .meta{{ font-size:11px; color:var(--muted); margin-top:4px; }}

  /* SCAN BUTTON */
  .scan-btn{{
    display:inline-flex; align-items:center; gap:7px;
    background:#1e3a5f; border:1px solid #3b82f6; border-radius:8px;
    padding:8px 16px; font-size:12px; font-weight:700; color:#93c5fd;
    cursor:pointer; text-decoration:none; transition:all .2s; white-space:nowrap;
    flex-shrink:0;
  }}
  .scan-btn:hover{{ background:#2563eb; color:#fff; border-color:#60a5fa; text-decoration:none; }}
  .scan-btn.loading{{ opacity:.7; cursor:wait; }}
  .spin{{ display:inline-block; animation:spin .8s linear infinite; }}
  @keyframes spin{{ to{{transform:rotate(360deg)}} }}

  /* TABS */
  .tabs{{ display:flex; flex-wrap:wrap; gap:5px; }}
  .tab{{
    background:transparent; border:1px solid var(--border); border-bottom:none;
    border-radius:8px 8px 0 0; padding:7px 13px; font-size:12px; font-weight:600;
    color:var(--muted); cursor:pointer; transition:all .15s;
    display:flex; align-items:center; gap:6px;
  }}
  .tab:hover{{ background:var(--surface2); color:var(--text); }}
  .tab.active{{ background:var(--bg); border-color:var(--accent); color:var(--accent); margin-bottom:-1px; }}
  .tab-count{{ background:var(--surface2); border-radius:10px; padding:1px 7px; font-size:10px; color:var(--muted); }}
  .tab.active .tab-count{{ background:#1e3a5f; color:var(--accent); }}
  .tab-border{{ border-bottom:1px solid var(--accent); margin:0 24px; }}

  /* LAYOUT */
  .container{{ max-width:960px; margin:0 auto; padding:20px 16px 60px; }}

  /* SECTION */
  .section{{ margin-bottom:24px; }}
  .section-title{{ font-size:14px; font-weight:700; padding:9px 14px;
                   border-radius:8px 8px 0 0; border:1px solid var(--border);
                   border-bottom:none; letter-spacing:0.5px; }}
  .section-construction .section-title{{ background:#0f1f1a; color:#34d399; border-color:#065f46; }}
  .section-manufacturing .section-title{{ background:#1a0f0f; color:#fb923c; border-color:#7c2d12; }}
  .section-hvac_mep .section-title{{ background:#0f1a2e; color:#60a5fa; border-color:#1e3a5f; }}
  .section-ai_tech .section-title{{ background:#1a0f2e; color:#a78bfa; border-color:#4c1d95; }}

  /* CARD */
  .card{{ background:var(--surface); border:1px solid var(--border);
          border-top:none; padding:14px 16px; transition:background .15s; }}
  .card:last-child{{ border-radius:0 0 8px 8px; }}
  .card:not(:last-child){{ border-bottom-color:var(--surface2); }}
  .card:hover{{ background:var(--surface2); }}
  .card-title{{ font-size:13.5px; font-weight:600; color:var(--text); line-height:1.4; margin-bottom:2px; }}
  .card-source{{ font-size:10px; color:var(--muted); margin-bottom:8px; }}

  /* BADGES */
  .badges{{ display:flex; flex-wrap:wrap; gap:5px; margin-bottom:10px; }}
  .badge{{ border-radius:4px; padding:2px 7px; font-size:10px; font-weight:600; border:1px solid; }}
  .badge-category{{ background:#1e293b; border-color:#334155; color:#94a3b8; }}
  .rel-high{{ background:#14532d; border-color:#16a34a; color:#fff; }}
  .rel-mid{{ background:#713f12; border-color:#d97706; color:#fff; }}
  .rel-low{{ background:#450a0a; border-color:#dc2626; color:#fff; }}
  .badge-depth{{ background:#1e1b4b; border-color:#4338ca; color:#a5b4fc; }}
  .badge-prac{{ background:#064e3b; border-color:#059669; color:#6ee7b7; }}
  .badge-prac-future{{ background:#1c1917; border-color:#78716c; color:#a8a29e; }}
  .badge-prac-research{{ background:#1f1035; border-color:#7c3aed; color:#c4b5fd; }}

  /* SUMMARY — rich multi-line */
  .summary{{ font-size:12.5px; color:#94a3b8; line-height:1.8; margin-bottom:8px; }}
  .summary p{{ padding:2px 0 2px 10px; border-left:2px solid var(--border); margin-bottom:4px; }}
  .summary p:first-child{{ border-color:#3b82f6; }}
  .summary p:nth-child(2){{ border-color:#10b981; }}
  .summary p:nth-child(3){{ border-color:#f59e0b; }}
  .summary p:nth-child(4){{ border-color:#8b5cf6; }}
  .summary p:nth-child(5){{ border-color:#ef4444; }}

  /* TAGS */
  .tags{{ display:flex; flex-wrap:wrap; gap:4px; margin-top:8px; }}
  .tag{{ background:#0f172a; border:1px solid #1e293b; border-radius:3px;
         padding:1px 6px; font-size:10px; color:var(--muted); }}

  /* FOOTER */
  .footer{{ text-align:center; padding:20px; font-size:11px; color:var(--muted);
            border-top:1px solid var(--border); margin-top:20px; }}
  .archive-link{{ text-align:right; font-size:11px; color:var(--muted); padding:8px 0 4px; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-top">
    <div>
      <h1>⚡ AI SIGNALS <span>SCAN</span></h1>
      <div class="meta">Cập nhật lúc {date_str} &nbsp;·&nbsp; {total} tín hiệu &nbsp;·&nbsp; Xây dựng · Sản xuất · Cơ điện lạnh</div>
    </div>
    <a class="scan-btn" href="{ACTIONS_URL}" target="_blank" id="scanBtn"
       onclick="handleScan(this)">
      <span id="scanIcon">⚡</span> Quét ngay
    </a>
  </div>
  <div class="tabs">{tab_buttons}</div>
</div>
<div class="tab-border"></div>

<div class="container">
  <div class="archive-link"><a href="archive/">📁 Bản tin cũ</a></div>
  <div id="sections">{sections_html}</div>
</div>

<div class="footer">
  AI Signals Scan &nbsp;·&nbsp; Powered by Gemini Flash + GitHub Actions
  &nbsp;·&nbsp; <a href="archive/">Kho lưu trữ</a>
</div>

<script>
  // Tab filter
  document.querySelectorAll('.tab').forEach(tab => {{
    tab.addEventListener('click', () => {{
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const domain = tab.dataset.domain;
      document.querySelectorAll('.section').forEach(sec => {{
        sec.style.display = (domain === 'all' || sec.dataset.domain === domain) ? '' : 'none';
      }});
    }});
  }});

  // Scan button — mở GitHub Actions, đổi icon thành loading
  function handleScan(el) {{
    el.classList.add('loading');
    document.getElementById('scanIcon').className = 'spin';
    document.getElementById('scanIcon').textContent = '⟳';
    setTimeout(() => {{
      el.classList.remove('loading');
      document.getElementById('scanIcon').className = '';
      document.getElementById('scanIcon').textContent = '⚡';
    }}, 4000);
  }}
</script>
</body>
</html>"""


def _section(domain: str, items: list) -> str:
    label = DOMAIN_LABELS.get(domain, domain)
    cards = "".join(_card(a) for a in items)
    return f"""
<div class="section section-{domain}" data-domain="{domain}">
  <div class="section-title">{label} &nbsp;·&nbsp; {len(items)} bài</div>
  {cards}
</div>"""


def _card(a: dict) -> str:
    title    = a.get("title", "")
    url      = a.get("url", "#")
    source   = a.get("source", "")
    pub      = a.get("published_at", "")[:10]
    category = a.get("category", "")
    tags     = a.get("tags", [])
    rel      = a.get("reliability_score", 0)
    depth    = a.get("depth", "")
    prac     = a.get("practicality", "")
    summary  = a.get("summary_vi", "")

    rel_class   = "rel-high" if rel >= 7 else ("rel-mid" if rel >= 5 else "rel-low")
    depth_label = DEPTH_LABELS.get(depth, depth)
    prac_label  = PRACTICALITY_LABELS.get(prac, prac)
    prac_class  = {"now":"badge-prac","near_future":"badge-prac-future",
                   "research":"badge-prac-research"}.get(prac, "badge-prac")

    summary_html = ""
    if summary:
        lines = [l.strip() for l in summary.split("\n") if l.strip()]
        summary_html = '<div class="summary">' + "".join(f"<p>{l}</p>" for l in lines) + "</div>"

    tags_html = ""
    if tags:
        tags_html = '<div class="tags">' + "".join(f'<span class="tag">{t}</span>' for t in tags) + "</div>"

    return f"""
<div class="card">
  <div class="card-title"><a href="{url}" target="_blank">{title}</a></div>
  <div class="card-source">{source} &nbsp;·&nbsp; {pub}</div>
  <div class="badges">
    <span class="badge badge-category">{category}</span>
    <span class="badge {rel_class}">★ {rel}/10</span>
    <span class="badge badge-depth">{depth_label}</span>
    <span class="badge {prac_class}">{prac_label}</span>
  </div>
  {summary_html}
  {tags_html}
</div>"""


def _update_archive_index():
    files = sorted(ARCHIVE_DIR.glob("*.html"), reverse=True)
    items = "".join(
        f'<li><a href="{f.name}">{f.stem.replace("_"," ")}</a></li>\n'
        for f in files
    )
    html = f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8"><title>Kho lưu trữ — AI Signals</title>
<style>
  body{{background:#0f1117;color:#e2e8f0;font-family:'Segoe UI',sans-serif;
       max-width:600px;margin:40px auto;padding:0 16px;}}
  h1{{color:#60a5fa;margin-bottom:20px;}}
  ul{{list-style:none;}}
  li{{padding:8px 0;border-bottom:1px solid #1e293b;}}
  a{{color:#93c5fd;text-decoration:none;}}
  a:hover{{text-decoration:underline;}}
  .back{{font-size:12px;margin-bottom:16px;}}
</style></head>
<body>
<div class="back"><a href="../index.html">← Bản tin mới nhất</a></div>
<h1>📁 Kho lưu trữ</h1>
<ul>{items}</ul>
</body></html>"""
    (ARCHIVE_DIR / "index.html").write_text(html, encoding="utf-8")
