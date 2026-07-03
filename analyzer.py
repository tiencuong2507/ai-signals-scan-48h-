import json
from google import genai
from config import GEMINI_API_KEY, MIN_RELIABILITY

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


ANALYSIS_PROMPT = """Bạn là chuyên gia phân tích công nghệ cho ngành xây dựng, sản xuất và cơ điện lạnh (MEP/HVAC) tại Việt Nam.

Phân tích nội dung sau và trả về JSON hợp lệ (không có markdown, không có text khác):

Tiêu đề: {title}
Nguồn: {source}
Nội dung: {summary}

Trả về JSON với các trường:
{{
  "relevant": true/false,
  "domain": "construction" | "manufacturing" | "hvac_mep" | "ai_tech",
  "category": "Tên chủ đề ngắn gọn (ví dụ: Robot hàn tự động, BIM 4D, AI dự đoán hỏng hóc...)",
  "tags": ["tag1", "tag2", "tag3", "tag4"],
  "reliability_score": 1-10,
  "depth": "shallow" | "medium" | "deep",
  "practicality": "now" | "near_future" | "research",
  "summary_vi": "Tóm tắt chi tiết tiếng Việt gồm 4-5 câu:\\n• Công nghệ/giải pháp: [mô tả cụ thể là gì, hoạt động thế nào]\\n• Kết quả/số liệu: [con số, hiệu quả đo được nếu có, nếu không có ghi N/A]\\n• Tại sao quan trọng: [lý do đáng chú ý với ngành XD/SX/cơ điện lạnh VN]\\n• Ứng dụng thực tế: [có thể áp dụng cụ thể như thế nào tại VN]\\n• Lưu ý: [rủi ro, hạn chế, hoặc điều cần cân nhắc nếu có]"
}}

Quy tắc đánh giá:
- relevant=true nếu bài liên quan đến AI/công nghệ trong XD/SX/Cơ điện lạnh, hoặc công nghệ nền tảng quan trọng (LLM, robotics, IoT, digital twin...)
- reliability_score: 9-10=peer-reviewed/nghiên cứu có data; 7-8=báo chuyên ngành uy tín; 5-6=tin tức kỹ thuật; 3-4=blog/thông cáo; 1-2=hype không có bằng chứng
- depth: deep=có methodology rõ ràng và số liệu; medium=phân tích khá chi tiết; shallow=mô tả chung chung
- practicality: now=công nghệ sẵn sàng thương mại; near_future=2-5 năm; research=còn trong nghiên cứu"""


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
