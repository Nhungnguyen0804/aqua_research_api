import re 
from rapidfuzz import fuzz
from src.utils import save_list_dict_to_csv

from src.state import LitState


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.lower().strip()
    doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
    return doi or None

def normalize_title(title: str | None) -> str | None:
    if not title:
        return None
    t = title.lower()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t or None

SOURCE_PRIORITY = {"openalex": 3, "core": 2, "arxiv": 1}


def dedup_node(state: LitState) -> LitState:
    papers = state.get("raw_papers", [])
    print(f"[dedup] input={len(papers)}")


SOURCE_PRIORITY = {
    "openalex": 3,
    "core": 2,
    "arxiv": 1
}

def merge_papers(paper1, paper2):

    priority1 = SOURCE_PRIORITY.get(paper1["source"], 0)
    priority2 = SOURCE_PRIORITY.get(paper2["source"], 0)

    # Chọn paper chính
    if priority1 >= priority2:
        primary = paper1
        secondary = paper2
    else:
        primary = paper2
        secondary = paper1

    merged = dict(primary)

    fields = [
        "abstract",
        "doi",
        "pdf_url",
        "venue",
        "journal",
        "reference_count"
    ]

    # Nếu paper chính thiếu thì lấy từ paper phụ
    for field in fields:
        if merged.get(field) is None:
            merged[field] = secondary.get(field)

    citation1 = paper1.get("citation_count")
    citation2 = paper2.get("citation_count")

    if citation1 is None:
        citation1 = 0

    if citation2 is None:
        citation2 = 0

    merged["citation_count"] = max(citation1, citation2)

    if merged["citation_count"] == 0:
        merged["citation_count"] = None

  
    categories = []
    if paper1.get("categories"):
        categories.extend(paper1["categories"])
    if paper2.get("categories"):
        categories.extend(paper2["categories"])
    merged["categories"] = list(set(categories))

    # Gộp source
    sources = []
    if paper1.get("sources"):
        sources.extend(paper1["sources"])
    else:
        sources.append(paper1["source"])
    if paper2.get("sources"):
        sources.extend(paper2["sources"])
    else:
        sources.append(paper2["source"])
    merged["sources"] = sorted(list(set(sources)))

    return merged


# co doi -> loai trung theo doi 
# ko doi => list khac 
def dedup_by_doi(papers):
    by_doi = {}
    no_doi = []

    for paper in papers:
        doi = normalize_doi(paper.get("doi"))
        if doi is None:
            no_doi.append(paper)
            continue
        if doi not in by_doi:
            by_doi[doi] = paper
        else:
            by_doi[doi] = merge_papers(by_doi[doi],paper)
    deduped = list(by_doi.values())
    return deduped, no_doi 

def find_similar_title(title, papers):

    for index, paper in enumerate(papers):
        old_title = normalize_title(paper.get("title"))

        if old_title is None:
            continue

        score = fuzz.token_sort_ratio(title,old_title)

        if score >= 92:
            return index

    return None

def dedup_by_title(deduped, no_doi):
    for paper in no_doi:
        title = normalize_title(paper.get("title"))
        if title is None:
            deduped.append(paper)
            continue

        match_index = find_similar_title(title,deduped)

        if match_index is None:
            deduped.append(paper)
        else:
            deduped[match_index] = merge_papers(deduped[match_index],paper)
    return deduped


def dedup_node(state):
    papers = state.get("raw_papers", [])
    print(f"[dedup] số báo ={len(papers)}")
    deduped, no_doi = dedup_by_doi(papers)
    deduped = dedup_by_title(deduped,no_doi)

    print(f"[dedup] số báo sau dedup ={len(deduped)}")
    # topic_dir
    topic_dir = 'data/topic_dir'
    path = f'{topic_dir}/deduped_papers.csv'
    save_list_dict_to_csv(deduped, path)
    state["deduped_papers"] = deduped
    return state