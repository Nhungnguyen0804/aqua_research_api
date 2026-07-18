

def build_query_expansion_prompt(query: str) -> list[dict]:
    system_text = (
        "Bạn là LitResearcher.\n"
        "Từ câu hỏi/chủ đề của người dùng (có thể là 1 topic ngắn hoặc câu hỏi dài mơ hồ), "
        "hãy hiểu đúng ý người dùng muốn tìm gì, rồi sinh ra 5-8 câu query tìm kiếm khác nhau "
        "(từ đồng nghĩa, viết tắt/đầy đủ, tiếng Anh học thuật, tiếng Việt nếu phù hợp) "
        "để tìm được nhiều bài báo liên quan nhất.\n"
        "Trả về JSON dạng: [\"query 1\", \"query 2\", ...]\n"
        "Chỉ trả JSON, không giải thích."
    )

    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": query}
    ]