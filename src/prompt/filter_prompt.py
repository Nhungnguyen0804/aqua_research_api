from src.utils import get_current_time

def build_search_messages(query: str):
    return [
        {
            "role": "system",
            "content": "You are a research assistant. Bạn tên là LitResearcher."
        },
        {
            "role": "system",
            "content": f"Thông tin bổ sung: Current time: {get_current_time()}"
        },
        {
            "role": "user",
            "content": query
        }
    ]


def build_prompt(query: str, papers: list[dict]) -> str:
    lines = []
    lines.append(f"Chủ đề nghiên cứu: {query}")
    lines.append("")
    lines.append("Với mỗi bài báo dưới đây, xác định bài đó có LIÊN QUAN trực tiếp đến chủ đề trên không.")
    lines.append('Trả lời CHỈ bằng JSON thuần, dạng: [{"index": 0, "relevant": true}, {"index": 1, "relevant": false}]')
    lines.append("Không giải thích, không markdown, không thêm chữ nào khác ngoài JSON.")
    lines.append("")

    for i, p in enumerate(papers):
        title = p.get("title") or ""
        abstract = p.get("abstract") or ""
        lines.append(f"[{i}] Title: {title}")
        lines.append(f"Abstract: {abstract[:500]}")
        lines.append("")

    return "\n".join(lines)

