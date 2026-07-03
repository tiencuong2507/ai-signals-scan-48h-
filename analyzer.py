import json
from google import genai
from config import GEMINI_API_KEY, MIN_RELIABILITY

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


ANALYSIS_PROMPT = """Bạn là chuyên gia phân tích công nghệ cho ngành xây dựng, sản xuất và cơ điện lạnh (MEP/HVAC).

Phân tích bài báo sau và trả về JSON hợp lệ (không có markdown, không có text khác):

Tiêu đề: {title}
Nguồn: {source}
Tóm tắt: {summary}

Trả về JSON với các trường:
{{
  "relevant": true/false,
  "domain": "construction" | "manufacturing" | "hvac_mep" | "ai_tech",
  "category": "Tên chủ đề ngắn gọn (ví dụ: Robot hàn tự động, BIM 4D, AI dự đoán hỏng hóc...)",
  "tags": ["tag1", "tag2", "tag3"],
  "reliability_score": 1-10,
  "depth": "shallow" | "medium" | "deep",
  "practicality": "now" | "near_future" | "research",
  "summary_vi": "• Là gì: [1 câu]\\n• Tại sao quan trọng: [1 câu]\\n• Có thể ứng dụng: [1 câu]"
}}

Quy tắc đánh giá:
- relevant=true nếu bài liên quan đến AI/công nghệ trong XD/SX/Cơ điện lạnh, hoặc là công nghệ nền tảng quan trọng
- reliability_score: 8-10 = nghiên cứu/tạp chí uy tín có dữ liệu; 5-7 = báo chuyên ngành; 1-4 = blog/hype/không có số liệu
- depth: deep = có methodology/số liệu cụ thể; medium = phân tích khá; shallow = mô tả chung chung
- practicality: now = có thể áp dụng ngay; near_future = 2-5 năm; research = còn trong lab"""


def analyze(article: dict) -> dict | None:
    prompt = ANALYSIS_PROMPT.format(
        title=article["title"],
        source=article["source"],
        summary=article["summary"],
    )
    try:
        response = _get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        raw = response.text.strip()

        # Xử lý trường hợp Gemini bọc JSON trong markdown code block
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)

        if not data.get("relevant"):
            return None
        if data.get("reliability_score", 0) < MIN_RELIABILITY:
            return None

        return {**article, **data}

    except json.JSONDecodeError:
        print(f"[WARN] JSON parse error for: {article['title'][:60]}")
        return None
    except Exception as e:
        print(f"[WARN] Analysis failed: {e}")
        return None
