import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

MAX_ARTICLES_PER_RUN = 60   # Giới hạn bài phân tích mỗi lần chạy
HOURS_BACK = 48             # Quét tin trong bao nhiêu giờ qua
MIN_RELIABILITY = 4         # Chỉ giữ bài có độ tin cậy >= X

RSS_SOURCES = [
    # ── AI & CÔNG NGHỆ ──────────────────────────────────────────────
    {"url": "https://venturebeat.com/category/ai/feed/",           "name": "VentureBeat AI",          "domain": "ai_tech"},
    {"url": "https://the-decoder.com/feed/",                       "name": "The Decoder",             "domain": "ai_tech"},
    {"url": "https://www.technologyreview.com/feed/",              "name": "MIT Technology Review",   "domain": "ai_tech"},
    {"url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "name": "Ars Technica Tech", "domain": "ai_tech"},
    {"url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "name": "The Verge AI", "domain": "ai_tech"},
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "name": "TechCrunch AI", "domain": "ai_tech"},

    # ── XÂY DỰNG ────────────────────────────────────────────────────
    {"url": "https://www.constructiondive.com/feeds/news/",        "name": "Construction Dive",       "domain": "construction"},
    {"url": "https://www.enr.com/rss/all",                         "name": "ENR",                     "domain": "construction"},
    {"url": "https://www.bdcnetwork.com/rss.xml",                  "name": "Building Design+Const.",  "domain": "construction"},
    {"url": "https://www.autodesk.com/blogs/construction/feed/",   "name": "Autodesk Construction",   "domain": "construction"},

    # ── SẢN XUẤT ────────────────────────────────────────────────────
    {"url": "https://www.industryweek.com/rss/all",                "name": "Industry Week",           "domain": "manufacturing"},
    {"url": "https://www.manufacturingnews.com/rss/",              "name": "Manufacturing News",      "domain": "manufacturing"},
    {"url": "https://www.assemblymag.com/rss/all",                 "name": "Assembly Magazine",       "domain": "manufacturing"},
    {"url": "https://www.sme.org/rss/",                            "name": "SME",                     "domain": "manufacturing"},

    # ── CƠ ĐIỆN LẠNH / MEP / HVAC ───────────────────────────────────
    {"url": "https://www.achrnews.com/rss/news",                   "name": "ACHR News",               "domain": "hvac_mep"},
    {"url": "https://www.contractingbusiness.com/rss/all",         "name": "Contracting Business",    "domain": "hvac_mep"},
    {"url": "https://www.hpacmag.com/feed/",                       "name": "HPAC Magazine",           "domain": "hvac_mep"},
    {"url": "https://www.ashrae.org/news/ashraejournal/rss",       "name": "ASHRAE Journal",          "domain": "hvac_mep"},

    # ── VIỆT NAM ─────────────────────────────────────────────────────
    {"url": "https://ictnews.vn/rss/home.rss",                     "name": "ICT News VN",             "domain": "ai_tech"},
    {"url": "https://vneconomy.vn/rss/cong-nghe.rss",              "name": "VnEconomy Công nghệ",     "domain": "ai_tech"},
]

DOMAIN_LABELS = {
    "construction": "🏗️ Xây dựng",
    "manufacturing": "🏭 Sản xuất",
    "hvac_mep":     "❄️ Cơ điện lạnh",
    "ai_tech":      "🤖 AI & Công nghệ",
}

DEPTH_LABELS = {
    "shallow": "📰 Bề mặt",
    "medium":  "📊 Trung bình",
    "deep":    "🔬 Chuyên sâu",
}

PRACTICALITY_LABELS = {
    "now":         "✅ Áp dụng ngay",
    "near_future": "⏳ 2–5 năm tới",
    "research":    "🧪 Nghiên cứu",
}
