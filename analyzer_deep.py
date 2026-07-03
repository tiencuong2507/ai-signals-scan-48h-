"""Deep scan mode — dùng Claude Sonnet, fetch full content, phân tích kỹ hơn."""
import json
import requests
from bs4 import BeautifulSoup
import anthropic
from config import ANTHROPIC_API_KEY, MIN_RELIABILITY

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _fetch_full(url: str) -> str:
    """Fetch và extract text từ bài viết gốc."""
    try:
        resp = requests.get(url, timeout=12, headers={
            "User-Agent": "Mozilla/5.0 (compatible; AISignalBot/1.0)"
        })
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        # Lấy 5000 ký tự đầu (đủ cho Claude phân tích)
        return "\n".join(line for line in text.splitlines() if len(line.strip()) > 30)[:5000]
    except Exception as e:
        return ""


DEEP_PROMPT = """Bạn là chuyên gia phân tích công nghệ cao cấp cho ngành xây dựng, sản xuất, và cơ điện lạnh (MEP/HVAC) tại Việt Nam.

Phân tích sâu nội dung sau. Trả về JSON hợp lệ (không markdown, không text khác):

Tiêu đề: {title}
Nguồn: {source}
URL: {url}
Nội dung đầy đủ:
{content}

Trả về JSON:
{{
  "relevant": true/false,
  "domain": "construction" | "manufacturing" | "hvac_mep" | "ai_tech",
  "category": "Tên chủ đề cụ thể",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "reliability_score": 1-10,
  "impact_score": 1-10,
  "depth": "shallow" | "medium" | "deep",
  "practicality": "now" | "near_future" | "research",
  "summary_vi": "• Công nghệ/giải pháp: [mô tả chi tiết công nghệ, cách hoạt động]\\n• Kết quả/số liệu: [số liệu cụ thể, KPI, benchmark đo được]\\n• Tại sao quan trọng: [tác động đến ngành XD/SX/cơ điện lạnh VN]\\n• Ứng dụng tại VN: [cách triển khai thực tế, ví dụ cụ thể]\\n• Lưu ý/rủi ro: [hạn chế, chi phí, điều cần cân nhắc]",
  "key_insight": "1 câu ngắn gọn nhất mô tả điểm đột phá hoặc điều quan trọng nhất",
  "action_items": ["Hành động 1 anh có thể làm ngay", "Hành động 2", "Hành động 3"]
}}

Tiêu chí đánh giá:
- reliability: 9-10=nghiên cứu peer-reviewed có data; 7-8=báo chuyên ngành uy tín; 5-6=tin kỹ thuật; 3-4=blog/thông cáo; 1-2=hype
- impact: 9-10=đột phá thay đổi ngành; 7-8=quan trọng đáng theo dõi; 5-6=hữu ích; 3-4=tham khảo; 1-2=ít liên quan
- action_items: phải cụ thể, thực tế, anh có thể làm được (tìm hiểu thêm, liên hệ vendor, thử pilot...)"""


def analyze(article: dict) -> dict | None:
    # Fetch full content
    full_content = _fetch_full(article["url"])
    content = full_content if len(full_content) > 200 else article.get("summary", "")

    prompt = DEEP_PROMPT.format(
        title=article["title"],
        source=article["source"],
        url=article["url"],
        content=content,
    )
    try:
        msg = _get_client().messages.create(
            model="claude-sonnet-5",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        # Tìm TextBlock theo type, bỏ qua ThinkingBlock
        text_block = next((b for b in msg.content if getattr(b, "type", "") == "text"), None)
        if not text_block:
            types = [getattr(b, "type", "?") for b in msg.content]
            print(f"[WARN] No text block (deep), got: {types} — {article['title'][:50]}")
            return None
        raw = (text_block.text or "").strip()
        # Extract JSON
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            print(f"[WARN] No JSON in response (deep): {raw[:120]!r}")
            return None
        raw = raw[start:end]

        data = json.loads(raw)
        if not data.get("relevant"):
            return None
        if data.get("reliability_score", 0) < MIN_RELIABILITY:
            return None

        return {**article, **data, "scan_mode": "deep"}

    except json.JSONDecodeError:
        print(f"[WARN] JSON parse error (deep): {article['title'][:60]}")
        return None
    except Exception as e:
        print(f"[WARN] Deep analysis failed: {e}")
        return None
