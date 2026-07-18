from datetime import datetime
from src.state import LitState

MIN_YEAR = datetime.now().year - 10   # bỏ bài cũ hơn 10 năm
BATCH_SIZE = 10      # số bài gửi mỗi lần gọi API

def check_condition_year(paper: dict) -> bool:
    year = paper.get("year")
    if year is None:
        return False
    if year >= MIN_YEAR:
        return True




def parse_relevance_response(text: str, expected_count: int) -> list[bool]:
    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        results = json.loads(cleaned)
    except Exception as e:
        print(f"[filter] parse JSON thất bại: {e} -> raw text: {cleaned[:200]}")
        return [True] * expected_count  # giữ lại hết nếu parse lỗi

    relevance_map = {}
    for r in results:
        relevance_map[r["index"]] = r["relevant"]

    flags = []
    for i in range(expected_count):
        flags.append(relevance_map.get(i, False))
    return flags

def check_relevance_batch(query: str, papers: list[dict]) -> list[bool]:
    prompt = build_prompt(query, papers)

    try:
        response = invoke_gemini(prompt)
    except Exception as e:
        print(f"[filter] Gemini call thất bại hoàn toàn: {e} -> giữ tất cả bài trong batch")
        return [True] * len(papers)

    return parse_relevance_response(response.content, len(papers))


def filter_node(state: LitState) -> LitState:
    papers = state.get("papers", [])
    query = state["query"]

    print(f"[filter] input={len(papers)}")

    # bước 1: lọc theo năm
    recent_papers = []
    for p in papers:
        if is_recent_enough(p):
            recent_papers.append(p)
    print(f"[filter] after year filter={len(recent_papers)}")

    # bước 2: lọc theo liên quan, gọi Gemini theo từng batch
    relevant_papers = []
    for i in range(0, len(recent_papers), BATCH_SIZE):
        batch = recent_papers[i:i + BATCH_SIZE]
        flags = check_relevance_batch(query, batch)

        for paper, is_rel in zip(batch, flags):
            if is_rel:
                relevant_papers.append(paper)

        time.sleep(1)  # tránh dồn request quá nhanh

    print(f"[filter] after relevance filter={len(relevant_papers)}")

    state["filtered_papers"] = relevant_papers
    return state