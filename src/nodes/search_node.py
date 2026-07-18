import arxiv
import requests
import time 

from src.state import LitState
from src.config import MY_GMAIL,CORE_API_KEY

def search_openalex(topic: str, max_results: int = 50) -> list[dict]:
    url = "https://api.openalex.org/works"
    params = {
        "search": topic,
        "per-page": min(max_results, 200),
        "mailto": MY_GMAIL,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("results", [])

    papers = []
    for p in data:
        authorships = p.get("authorships") or []
        primary_loc = p.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        oa = p.get("open_access") or {}

        # ghép abstract từ inverted index -> text thường
        inv = p.get("abstract_inverted_index")
        abstract = None
        if inv:
            positions = {}
            for word, idxs in inv.items():
                for i in idxs:
                    positions[i] = word
            abstract = " ".join(positions[i] for i in sorted(positions))

        papers.append({
            "source": "openalex",
            "paper_id": p.get("id"),
            "title": p.get("title"),
            "abstract": abstract,
            "authors": [a.get("author", {}).get("display_name") for a in authorships],
            "year": p.get("publication_year"),
            "publication_date": p.get("publication_date"),
            "doi": p.get("doi"),
            "url": p.get("id"),
            "pdf_url": oa.get("oa_url"),
            "venue": source.get("display_name"),
            "journal": source.get("display_name"),
            "citation_count": p.get("cited_by_count"),
            "reference_count": len(p.get("referenced_works") or []),
            "categories": [c.get("display_name") for c in (p.get("concepts") or [])],
        })
    return papers


def search_arxiv(topic:str) -> list[dict]:
    client = arxiv.Client()
    search = arxiv.Search(query=topic, max_results=50, sort_by=arxiv.SortCriterion.Relevance)
    results = client.results(search)

    papers = []
    for paper in results:
        papers.append({
            "source": "arxiv",
            "paper_id": paper.get_short_id(),
            "title": paper.title,
            "abstract": paper.summary,
            "authors": [a.name for a in paper.authors],
            "year": paper.published.year,
            "publication_date": paper.published.isoformat(),
            "doi": paper.doi,
            "url": paper.entry_id,
            "pdf_url": paper.pdf_url,
            "venue": None,
            "journal": paper.journal_ref,
            "citation_count": None,
            "reference_count": None,
            "categories": paper.categories,
        })
    return papers

def search_core(topic: str, max_results: int = 10, api_key: str = CORE_API_KEY) -> list[dict]:
    url = "https://api.core.ac.uk/v3/search/works"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "q": topic,
        "limit": min(max_results, 100),
    }
    resp = requests.get(url, headers=headers, params=params, timeout=300)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    papers = []
    for p in results:
        authors = [a.get("name") for a in (p.get("authors") or [])]
        urls = p.get("sourceFulltextUrls") or [None]
        papers.append({
            "source": "core",
            "paper_id": p.get("id"),
            "title": p.get("title"),
            "abstract": p.get("abstract"),
            "authors": authors,
            "year": p.get("yearPublished"),
            "publication_date": p.get("publishedDate"),
            "doi": p.get("doi"),
            "url": p.get("downloadUrl") or urls[0],
            "pdf_url": p.get("downloadUrl"),
            "venue": p.get("publisher"),
            "journal": p.get("publisher"),
            "citation_count": p.get("citationCount"),
            "reference_count": None,
            "categories": p.get("fieldOfStudy") or [],
        })
    return papers

def search_node(state: LitState) -> LitState:
    print(f"[search] query={state['topic']}")
    query = state['topic']
    sub_queries = state.get("sub_queries", [])
    print(f"[search] sub_queries={state['sub_queries']}")
    if not sub_queries:
        sub_queries = query

    all_papers = []
    for sub_query in sub_queries:
        papers_arxiv = search_arxiv(sub_query)
        papers_openalex = search_openalex(sub_query)
        papers_core = search_core(sub_query)
    
        all_papers.extend(papers_arxiv)  
        all_papers.extend(papers_openalex)
        all_papers.extend(papers_core)
    state['raw_papers'] = all_papers
    return state 
