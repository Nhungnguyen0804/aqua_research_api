from src.utils import get_current_time

DEFAULT_TEXT = f'''
    Bạn là LitResearcher.\n
    Thông tin tôi bổ sung cho bạn là: Current time: {get_current_time()}
'''

def build_rq_rico_prompt(topic: str) -> list[dict]:
    system_text = f'''
        {DEFAULT_TEXT}
        Từ topic sau, hãy xác định PICO và sinh 1 research question rõ ràng cho một Systematic Literature Review.
    '''
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": f'Topic: {topic}'}
    ]

def build_query_expansion_prompt(query: str) -> list[dict]:
    system_text = f'''
        {DEFAULT_TEXT}
        Từ câu hỏi/chủ đề của người dùng (có thể là 1 topic ngắn hoặc câu hỏi dài mơ hồ), 
        hãy hiểu đúng ý người dùng muốn tìm gì, rồi sinh ra 5-8 câu query tìm kiếm khác nhau 
        (từ đồng nghĩa, viết tắt/đầy đủ, tiếng Anh học thuật, tiếng Việt nếu phù hợp) 
        để tìm được nhiều bài báo liên quan nhất.\n
        Trả về JSON dạng: [\"query 1\", \"query 2\", ...]\n
        Chỉ trả JSON, không giải thích.
    '''

    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": query}
    ]


def build_filter_prompt(pico: dict, papers: list[dict]) -> list[dict]:
    system_text = f'''
        {DEFAULT_TEXT}
        Tiêu chí Eligibility (PICO) để đánh giá bài báo có nên đưa vào Systematic Literature Review:
        - Population: {pico['population']}
        - Intervention: {pico['intervention']}
        - Comparison: {pico['comparison']}
        - Outcome: {pico['outcome']}

        Với mỗi bài báo trong danh sách JSON dưới đây (gồm title, abstract),
        đánh giá bài đó có phù hợp với TẤT CẢ các tiêu chí PICO trên hay không.
        Trả về JSON dạng: [{{"id": "...", "relevant": true/false, "reason": "..."}}]
        Chỉ trả JSON, không giải thích thêm ngoài JSON.
    '''
    import json
    papers_text = json.dumps(papers, ensure_ascii=False)
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": papers_text}
    ]