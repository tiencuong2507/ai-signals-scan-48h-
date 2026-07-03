import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SCAN_MODE         = os.getenv("SCAN_MODE", "fast")   # "fast" | "deep"
GH_DISPATCH_TOKEN = os.getenv("GH_DISPATCH_TOKEN", "")  # Fine-grained PAT, Actions R/W only

MAX_ARTICLES_PER_RUN = 80   # fast mode
MAX_ARTICLES_DEEP    = 30   # deep mode (Claude, tốn hơn)
HOURS_BACK = 24
MIN_RELIABILITY = 4

# Keyword pre-filter — bài phải chứa ít nhất 1 từ khóa này (title + summary)
RELEVANT_KEYWORDS = [
    # AI / Công nghệ nền tảng
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "robot", "automation", "computer vision", "neural", "model",
    "sensor", "iot", "digital twin", "software", "algorithm", "data",
    # Xây dựng
    "construction", "building", "bim", "architect", "prefab", "concrete",
    "structural", "infrastructure", "smart building", "modular", "drone",
    # Sản xuất
    "manufactur", "factory", "production", "industry 4", "cnc", "quality",
    "supply chain", "assembly", "welding", "3d print", "additive",
    # Cơ điện lạnh / MEP
    "hvac", "heating", "cooling", "ventilation", "refrigerat", "mep",
    "mechanical", "energy efficiency", "chiller", "heat pump", "vrf",
    "compressor", "insulation", "thermal", "electr",
    # GitHub repos
    "github", "⭐",
]

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
