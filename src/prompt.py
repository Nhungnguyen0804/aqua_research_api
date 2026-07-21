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

def build_extract_prompt(paper: dict) -> list[dict]:
    text = paper.get("full_text") or paper.get("abstract") or ""
    title = paper.get("title", "")

    system_prompt = f'''
        {DEFAULT_TEXT}
        Bạn là trợ lý nghiên cứu khoa học. Đọc nội dung bài báo và trích xuất chính xác 
        contribution, method, limitation, key findings. Chỉ dựa trên nội dung được cung cấp, 
        không suy đoán ngoài văn bản. Nếu không đủ thông tin cho 1 mục, ghi 'Không đủ thông tin'.
    '''
    user_prompt = f"Title: {title}\n\nNội dung bài báo:\n{text}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_review_prompt(paper: dict) -> list[dict]:
    text = paper.get("full_text") or ""
    system_prompt = f'''
        Bạn là reviewer kiểm tra chất lượng trích xuất. So sánh phần 
        'Extracted Info' với 'Source Text'. Đánh giá xem contribution, method, 
        limitation, key_findings có được nội dung gốc hỗ trợ (grounded) không, 
        hay là suy diễn/bịa đặt (hallucinated). Nếu bất kỳ mục nào không có 
        căn cứ rõ ràng trong source text, đánh dấu is_grounded=False và nêu rõ mục nào có vấn đề trong 'issues'.
    '''
    user_prompt = (
        f"Source Text:\n{text}\n\n"
        f"Extracted Info:\n"
        f"- Contribution: {paper.get('contribution')}\n"
        f"- Method: {paper.get('method')}\n"
        f"- Limitation: {paper.get('limitation')}\n"
        f"- Key Findings: {paper.get('key_findings')}\n"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]