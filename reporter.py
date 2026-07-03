import os
import re
from datetime import datetime
from pathlib import Path
from config import DOMAIN_LABELS, DEPTH_LABELS, PRACTICALITY_LABELS


# Highlight số liệu, %, tỷ/triệu/billion/million trong summary
_NUM_RE = re.compile(
    r'(\b\d[\d,\.]*\s*(?:%|tỷ|triệu|billion|million|MW|GW|km²?|m²|USD|VNĐ|lần|x\d)\b'
    r'|\b\d{2,}[\d,\.]*\b)',
    re.IGNORECASE
)

def _highlight(text: str) -> str:
    """Bold số liệu và wrap từ khóa quan trọng."""
    text = _NUM_RE.sub(r'<strong class="hl-num">\1</strong>', text)
    # highlight nội dung trong ngoặc kép
    text = re.sub(r'"([^"]{3,60})"', r'"<em class="hl-quote">\1</em>"', text)
    return text

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
        items.sort(key=lambda x: (x.get("impact_score", 0) + x.get("reliability_score", 0)), reverse=True)
        sections_html += _section(domain, items)

    date_str = run_time.strftime("%d/%m/%Y %H:%M UTC")
    total = len(articles)
    counts = {d: len(grouped.get(d, [])) for d in domain_order}

    tab_buttons = f'<button class="tab active" data-domain="all">🔎 Tất cả <span class="tab-count">{total}</span></button>'
    for d in domain_order:
        if counts[d]:
            label = DOMAIN_LABELS.get(d, d)
            tab_buttons += f'<button class="tab" data-domain="{d}">{label} <span class="tab-count">{counts[d]}</span></button>'
    tab_buttons += '<button class="tab" data-domain="saved" id="savedTab">⭐ Đã lưu <span class="tab-count" id="savedCount">0</span></button>'

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
        font-size:16px; line-height:1.7; }}
  a{{ color:var(--accent); text-decoration:none; }}
  a:hover{{ text-decoration:underline; }}

  /* HEADER */
  .header{{ background:linear-gradient(135deg,#0f1b3d 0%,#1a0f2e 100%);
            border-bottom:1px solid var(--border); padding:22px 24px 0; }}
  .header-top{{ display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px; }}
  .header h1{{ font-size:24px; font-weight:800; color:#fff; letter-spacing:1px; }}
  .header h1 span{{ color:var(--accent); }}
  .header .meta{{ font-size:13px; color:var(--muted); margin-top:5px; }}

  /* SCAN BUTTON */
  .scan-btn{{
    display:inline-flex; align-items:center; gap:7px;
    background:#1e3a5f; border:1px solid #3b82f6; border-radius:8px;
    padding:10px 18px; font-size:14px; font-weight:700; color:#93c5fd;
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
    border-radius:8px 8px 0 0; padding:8px 15px; font-size:13px; font-weight:600;
    color:var(--muted); cursor:pointer; transition:all .15s;
    display:flex; align-items:center; gap:6px;
  }}
  .tab:hover{{ background:var(--surface2); color:var(--text); }}
  .tab.active{{ background:var(--bg); border-color:var(--accent); color:var(--accent); margin-bottom:-1px; }}
  .tab-count{{ background:var(--surface2); border-radius:10px; padding:1px 8px; font-size:11px; color:var(--muted); }}
  .tab.active .tab-count{{ background:#1e3a5f; color:var(--accent); }}
  .tab-border{{ border-bottom:1px solid var(--accent); margin:0 24px; }}

  /* LAYOUT */
  .container{{ max-width:980px; margin:0 auto; padding:22px 18px 60px; }}

  /* SECTION */
  .section{{ margin-bottom:28px; }}
  .section-title{{ font-size:16px; font-weight:700; padding:11px 16px;
                   border-radius:8px 8px 0 0; border:1px solid var(--border);
                   border-bottom:none; letter-spacing:0.5px; }}
  .section-construction .section-title{{ background:#0f1f1a; color:#34d399; border-color:#065f46; }}
  .section-manufacturing .section-title{{ background:#1a0f0f; color:#fb923c; border-color:#7c2d12; }}
  .section-hvac_mep .section-title{{ background:#0f1a2e; color:#60a5fa; border-color:#1e3a5f; }}
  .section-ai_tech .section-title{{ background:#1a0f2e; color:#a78bfa; border-color:#4c1d95; }}

  /* CARD */
  .card{{ background:var(--surface); border:1px solid var(--border);
          border-top:none; padding:18px 20px; transition:background .15s; }}
  .card:last-child{{ border-radius:0 0 8px 8px; }}
  .card:not(:last-child){{ border-bottom-color:var(--surface2); }}
  .card:hover{{ background:var(--surface2); }}
  .card-title{{ font-size:16px; font-weight:700; color:var(--text); line-height:1.45; margin-bottom:4px; }}
  .card-source{{ font-size:12px; color:var(--muted); margin-bottom:10px; }}

  /* BADGES */
  .badges{{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px; }}
  .badge{{ border-radius:5px; padding:3px 9px; font-size:11px; font-weight:600; border:1px solid; }}
  .badge-category{{ background:#1e293b; border-color:#334155; color:#cbd5e1; }}
  .rel-high{{ background:#14532d; border-color:#16a34a; color:#fff; }}
  .rel-mid{{ background:#713f12; border-color:#d97706; color:#fff; }}
  .rel-low{{ background:#450a0a; border-color:#dc2626; color:#fff; }}
  .badge-depth{{ background:#1e1b4b; border-color:#4338ca; color:#a5b4fc; }}
  .badge-prac{{ background:#064e3b; border-color:#059669; color:#6ee7b7; }}
  .badge-prac-future{{ background:#1c1917; border-color:#78716c; color:#a8a29e; }}
  .badge-prac-research{{ background:#1f1035; border-color:#7c3aed; color:#c4b5fd; }}
  .badge-impact-high{{ background:#1a2f1a; border-color:#f59e0b; color:#fbbf24; }}
  .badge-impact-mid{{ background:#1a1a2f; border-color:#6366f1; color:#a5b4fc; }}
  .badge-impact-low{{ background:#1f1f1f; border-color:#475569; color:#94a3b8; }}

  /* SUMMARY — rich multi-line */
  .summary{{ font-size:14px; color:#b0bfd0; line-height:1.85; margin-bottom:10px; }}

  /* Dòng đầu tiên: highlight box nổi bật */
  .summary p.line-first{{
    background:linear-gradient(90deg,#0f2744 0%,#0f1f3d 100%);
    border-left:3px solid #3b82f6;
    border-radius:0 6px 6px 0;
    padding:8px 12px;
    margin-bottom:7px;
    font-size:15px;
    font-weight:600;
    color:#e2e8f0;
  }}
  /* Dòng tiếp theo */
  .summary p.line-other{{
    padding:3px 0 3px 12px;
    border-left:2px solid var(--border);
    margin-bottom:5px;
    color:#94a3b8;
  }}
  .summary p.line-other:nth-child(2){{ border-color:#10b981; }}
  .summary p.line-other:nth-child(3){{ border-color:#f59e0b; color:#b0bfd0; }}
  .summary p.line-other:nth-child(4){{ border-color:#8b5cf6; }}
  .summary p.line-other:nth-child(5){{ border-color:#ef4444; }}

  /* Highlight số liệu trong text */
  .hl-num{{ color:#fbbf24; font-weight:700; font-style:normal; }}
  .hl-quote{{ color:#86efac; font-style:italic; }}

  /* TAGS */
  .tags{{ display:flex; flex-wrap:wrap; gap:5px; margin-top:10px; }}
  .tag{{ background:#0f172a; border:1px solid #1e293b; border-radius:4px;
         padding:2px 8px; font-size:11px; color:var(--muted); }}

  /* KEY INSIGHT (deep mode) */
  .key-insight{{
    background:linear-gradient(90deg,#1a1500 0%,#1f1a05 100%);
    border-left:3px solid #f59e0b; border-radius:0 6px 6px 0;
    padding:8px 12px; margin-bottom:8px;
    font-size:14px; font-weight:700; color:#fde68a;
  }}
  .key-insight::before{{ content:"💎 "; }}

  /* ACTION ITEMS (deep mode) */
  .action-items{{ margin-top:10px; }}
  .action-items-title{{ font-size:11px; font-weight:700; color:#6ee7b7; text-transform:uppercase;
                         letter-spacing:1px; margin-bottom:6px; }}
  .action-item{{ display:flex; gap:8px; align-items:flex-start; padding:4px 0;
                 font-size:13px; color:#94a3b8; }}
  .action-item::before{{ content:"→"; color:#34d399; font-weight:700; flex-shrink:0; }}

  /* BOOKMARK BUTTON */
  .card-top{{ display:flex; align-items:flex-start; justify-content:space-between; gap:8px; }}
  .bookmark-btn{{
    background:none; border:1px solid var(--border); border-radius:6px;
    padding:4px 8px; cursor:pointer; font-size:16px; color:var(--muted);
    transition:all .2s; flex-shrink:0; line-height:1;
  }}
  .bookmark-btn:hover{{ border-color:#f59e0b; color:#f59e0b; background:#1a1500; }}
  .bookmark-btn.saved{{ border-color:#f59e0b; color:#f59e0b; background:#1a1500; }}

  /* SAVED TAB SECTION */
  #saved-section{{ display:none; }}
  .saved-empty{{ text-align:center; color:var(--muted); padding:40px 20px; font-size:15px; }}
  .saved-card{{
    background:var(--surface); border:1px solid #f59e0b33; border-radius:8px;
    padding:14px 16px; margin-bottom:10px; position:relative;
  }}
  .saved-card-title{{ font-size:15px; font-weight:700; margin-bottom:4px; }}
  .saved-card-meta{{ font-size:12px; color:var(--muted); margin-bottom:8px; }}
  .saved-card-summary{{ font-size:13px; color:#94a3b8; line-height:1.7; }}
  .unsave-btn{{
    position:absolute; top:12px; right:12px;
    background:none; border:none; cursor:pointer; font-size:18px; color:#f59e0b;
  }}
  .unsave-btn:hover{{ color:#ef4444; }}
  .saved-header{{ display:flex; align-items:center; justify-content:space-between;
                   margin-bottom:14px; }}
  .saved-header h2{{ font-size:16px; font-weight:700; color:#f59e0b; }}
  .clear-all-btn{{
    background:none; border:1px solid #dc2626; border-radius:6px;
    padding:4px 10px; font-size:12px; color:#f87171; cursor:pointer;
  }}
  .clear-all-btn:hover{{ background:#450a0a; }}

  /* FOOTER */
  .footer{{ text-align:center; padding:24px; font-size:13px; color:var(--muted);
            border-top:1px solid var(--border); margin-top:20px; }}
  .archive-link{{ text-align:right; font-size:12px; color:var(--muted); padding:10px 0 6px; }}
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
  <div id="saved-section">
    <div class="saved-header">
      <h2>⭐ Bài viết đã lưu</h2>
      <button class="clear-all-btn" onclick="clearAllSaved()">Xóa tất cả</button>
    </div>
    <div id="saved-list"></div>
  </div>
</div>

<div class="footer">
  AI Signals Scan &nbsp;·&nbsp; Powered by Gemini Flash + GitHub Actions
  &nbsp;·&nbsp; <a href="archive/">Kho lưu trữ</a>
</div>

<script>
  // ── BOOKMARK SYSTEM ──────────────────────────────────────────────
  const STORE = 'ai_signals_saved';

  function getSaved() {{
    try {{ return JSON.parse(localStorage.getItem(STORE) || '{{}}'); }}
    catch {{ return {{}}; }}
  }}

  function setSaved(data) {{
    localStorage.setItem(STORE, JSON.stringify(data));
  }}

  function toggleBookmark(url, title, source, date, summary) {{
    const saved = getSaved();
    if (saved[url]) {{
      delete saved[url];
    }} else {{
      saved[url] = {{ url, title, source, date, summary, savedAt: new Date().toLocaleDateString('vi-VN') }};
    }}
    setSaved(saved);
    refreshBookmarkStates();
    if (document.getElementById('saved-section').style.display !== 'none') renderSaved();
  }}

  function refreshBookmarkStates() {{
    const saved = getSaved();
    const count = Object.keys(saved).length;
    document.getElementById('savedCount').textContent = count;
    document.querySelectorAll('.bookmark-btn').forEach(btn => {{
      const url = btn.dataset.url;
      if (saved[url]) {{ btn.classList.add('saved'); btn.title = 'Bỏ lưu'; btn.textContent = '⭐'; }}
      else {{ btn.classList.remove('saved'); btn.title = 'Lưu bài'; btn.textContent = '☆'; }}
    }});
  }}

  function renderSaved() {{
    const saved = getSaved();
    const list = document.getElementById('saved-list');
    const entries = Object.values(saved).reverse();
    if (!entries.length) {{
      list.innerHTML = '<div class="saved-empty">Chưa có bài nào được lưu.<br>Bấm ☆ trên bài viết để lưu.</div>';
      return;
    }}
    list.innerHTML = entries.map(a => `
      <div class="saved-card">
        <button class="unsave-btn" onclick="toggleBookmark('${{a.url}}','${{a.title}}','${{a.source}}','${{a.date}}','${{a.summary}}')" title="Bỏ lưu">⭐</button>
        <div class="saved-card-title"><a href="${{a.url}}" target="_blank">${{a.title}}</a></div>
        <div class="saved-card-meta">${{a.source}} · ${{a.date}} · Đã lưu ${{a.savedAt}}</div>
        <div class="saved-card-summary">${{a.summary.replace(/\\n/g,'<br>')}}</div>
      </div>`).join('');
  }}

  function clearAllSaved() {{
    if (confirm('Xóa tất cả bài đã lưu?')) {{
      setSaved({{}});
      refreshBookmarkStates();
      renderSaved();
    }}
  }}

  // ── TAB FILTER ───────────────────────────────────────────────────
  document.querySelectorAll('.tab').forEach(tab => {{
    tab.addEventListener('click', () => {{
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const domain = tab.dataset.domain;
      const sectionsEl = document.getElementById('sections');
      const savedEl = document.getElementById('saved-section');
      if (domain === 'saved') {{
        sectionsEl.style.display = 'none';
        savedEl.style.display = '';
        renderSaved();
      }} else {{
        sectionsEl.style.display = '';
        savedEl.style.display = 'none';
        document.querySelectorAll('.section').forEach(sec => {{
          sec.style.display = (domain === 'all' || sec.dataset.domain === domain) ? '' : 'none';
        }});
      }}
    }});
  }});

  // ── SCAN BUTTON ──────────────────────────────────────────────────
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

  // Init
  refreshBookmarkStates();
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

    impact      = a.get("impact_score", 0)
    rel_class   = "rel-high" if rel >= 7 else ("rel-mid" if rel >= 5 else "rel-low")
    depth_label = DEPTH_LABELS.get(depth, depth)
    prac_label  = PRACTICALITY_LABELS.get(prac, prac)
    prac_class  = {"now":"badge-prac","near_future":"badge-prac-future",
                   "research":"badge-prac-research"}.get(prac, "badge-prac")
    impact_class = "badge-impact-high" if impact >= 7 else ("badge-impact-mid" if impact >= 5 else "badge-impact-low")
    impact_label = f"🔥 Tác động {impact}/10" if impact >= 7 else f"💡 Tác động {impact}/10"

    summary_html = ""
    if summary:
        lines = [l.strip() for l in summary.split("\n") if l.strip()]
        parts = []
        for i, line in enumerate(lines):
            cls = "line-first" if i == 0 else "line-other"
            parts.append(f'<p class="{cls}">{_highlight(line)}</p>')
        summary_html = '<div class="summary">' + "".join(parts) + "</div>"

    tags_html = ""
    if tags:
        tags_html = '<div class="tags">' + "".join(f'<span class="tag">{t}</span>' for t in tags) + "</div>"

    # Deep mode extras
    key_insight = a.get("key_insight", "")
    action_items = a.get("action_items", [])
    is_deep = a.get("scan_mode") == "deep"

    key_insight_html = f'<div class="key-insight">{key_insight}</div>' if key_insight else ""

    actions_html = ""
    if action_items:
        items_html = "".join(f'<div class="action-item">{item}</div>' for item in action_items)
        actions_html = f'<div class="action-items"><div class="action-items-title">Hành động gợi ý</div>{items_html}</div>'

    deep_badge = '<span class="badge" style="background:#0f2744;border-color:#3b82f6;color:#60a5fa;">🔬 Deep</span>' if is_deep else ""

    # Escape summary for JS attribute
    summary_js = summary.replace("'", "\\'").replace('"', '&quot;').replace("\n", "\\n")[:300]

    return f"""
<div class="card">
  <div class="card-top">
    <div style="flex:1">
      <div class="card-title"><a href="{url}" target="_blank">{title}</a></div>
      <div class="card-source">{source} &nbsp;·&nbsp; {pub}</div>
    </div>
    <button class="bookmark-btn" data-url="{url}"
      onclick="toggleBookmark('{url}','{title.replace(chr(39), '').replace(chr(34), '')}','{source}','{pub}','{summary_js}')"
      title="Lưu bài">☆</button>
  </div>
  <div class="badges">
    {deep_badge}
    <span class="badge badge-category">{category}</span>
    <span class="badge {impact_class}">{impact_label}</span>
    <span class="badge {rel_class}">★ Tin cậy {rel}/10</span>
    <span class="badge badge-depth">{depth_label}</span>
    <span class="badge {prac_class}">{prac_label}</span>
  </div>
  {key_insight_html}
  {summary_html}
  {actions_html}
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
