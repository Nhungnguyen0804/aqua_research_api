from copy import deepcopy
from src.services.embedding import embed_text, embed_text_list, compute_similarity
from datetime import datetime
from src.state import LitState
SKIP_YEAR = 5
MIN_YEAR = datetime.now().year - SKIP_YEAR  # bỏ bài cũ hơn 10 năm


def check_condition_year(paper: dict) -> bool:
    year = paper.get("year")
    if year is None:
        return False
    if year >= MIN_YEAR:
        return True

def build_pico_query_text(pico):
    return " ".join([
        pico.population,
        pico.intervention,
        pico.comparison,
        pico.outcome,
    ])


def build_info_paper_text(paper: dict) -> str:
    """Ghép title + abstract của 1 paper thành text để embed."""
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    return f"{title}. {abstract}"

def rank_papers_by_similarity(pico, papers):
    pico_text = build_pico_query_text(pico)
    pico_embedding = embed_text(pico_text)

    paper_texts = []
    for paper in papers:
        paper_texts.append(build_info_paper_text(paper))

    paper_embeddings = embed_text_list(paper_texts)
    scores = compute_similarity(pico_embedding, paper_embeddings)

    results = []
    for i in range(len(papers)):
        results.append((papers[i], scores[i]))

    results.sort(key=lambda item: item[1], reverse=True)

    return results


def select_by_threshold(ranked_papers, threshold: float = 0.35) -> list[dict]:
    # giữ lại các bài có cosine similarity ≥ 0.35 với PICO query
    result = []
    for paper, score in ranked_papers:
        if score >= threshold:
            p = deepcopy(paper)
            p["similarity_score"] = round(score, 4)
            result.append(p)
    return result


def screen_node(state: LitState) -> LitState:
    deduped_papers = state.get('deduped_papers')
    print(f'[filter] min year (hiện tại - {SKIP_YEAR} năm) = ', MIN_YEAR)
    
    year_filtered = []
    for paper in deduped_papers:
        if check_condition_year(paper):
            year_filtered.append(paper)
    
    print(f'[filter] số lượng paper lọc theo năm: {len(year_filtered)}' )

    pico = state.get('research_question')
    print(f'[filter] pico = {pico}')

    ranked = rank_papers_by_similarity(pico, year_filtered)

    screened = select_by_threshold(ranked)
    print(f'[screen] số lượng paper sau semantic screening: {len(screened)}')
    state['screened_papers'] = screened
    return state 


