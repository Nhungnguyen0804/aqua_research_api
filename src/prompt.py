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

def build_eligibility_criteria_prompt(pico, research_question: str) -> list[dict]:
    system_text = f'''
        {DEFAULT_TEXT}
        Research question: {research_question}
        PICO:
        - Population: {pico.population}
        - Intervention: {pico.intervention}
        - Comparison: {pico.comparison}
        - Outcome: {pico.outcome}

        Hãy đề xuất tiêu chí Eligibility (Inclusion/Exclusion criteria) phù hợp cho 
        Systematic Literature Review với PICO trên, theo chuẩn PRISMA 2020.
        Tiêu chí phải cụ thể, khả thi để đánh giá chỉ dựa trên title+abstract.
        Trả về JSON dạng:
        {{
            "inclusion_criteria": ["...", "..."],
            "exclusion_criteria": ["...", "..."]
        }}
    '''
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": research_question}
    ]


def build_eligibility_prompt(criteria, papers: list[dict]) -> list[dict]:
    papers_for_llm = [
        {"id": str(i), "title": p.get("title", ""), "abstract": p.get("abstract", "")}
        for i, p in enumerate(papers)
    ]

    inclusion_text = "\n".join(f"- {c}" for c in criteria.inclusion_criteria)
    exclusion_text = "\n".join(f"- {c}" for c in criteria.exclusion_criteria)

    system_text = f'''
        {DEFAULT_TEXT}
        Tiêu chí Inclusion (phải thỏa mãn để đưa vào):
        {inclusion_text}

        Tiêu chí Exclusion (có 1 trong các điều sau thì loại):
        {exclusion_text}

        Nếu KHÔNG CHẮC CHẮN (abstract mơ hồ, thiếu thông tin), LOẠI RA (relevant=false).
        Reason tối đa 15 từ, nêu rõ dựa vào tiêu chí nào.
        Trả về JSON: [{{"id": "...", "relevant": true/false, "reason": "..."}}]
    '''
    import json
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": json.dumps(papers_for_llm, ensure_ascii=False)}
    ]

