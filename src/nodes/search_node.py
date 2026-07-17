from langgraph.graph import StateGraph, END
from semanticscholar import SemanticScholar
import arxiv
from src.state import LitState


# def search_semantic_scholar(topic: str) -> list[dict]:
#     sch = SemanticScholar()
#     results = sch.search_paper(topic, limit=50)

#     papers = []

#     for paper in results:
#         d = paper._data

#         external_ids = d.get("externalIds") or {}
#         open_access = d.get("openAccessPdf") or {}

#         papers.append({
#             "source": "semantic_scholar",
#             "paper_id": d.get("paperId"),
#             "title": d.get("title"),
#             "abstract": d.get("abstract"),
#             "authors": [a["name"] for a in d.get("authors", [])],
#             "year": d.get("year"),
#             "publication_date": d.get("publicationDate"),
#             "doi": external_ids.get("DOI"),
#             "url": d.get("url"),
#             "pdf_url": open_access.get("url"),
#             "venue": d.get("venue"),
#             "journal": d.get("journal"),
#             "citation_count": d.get("citationCount"),
#             "reference_count": d.get("referenceCount"),
#             "categories": d.get("fieldsOfStudy", []),
#         })

#     return papers

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

    
def search_node(state: LitState) -> LitState:
    print(f"[search] query={state['query']}")
    query = state['query']

    papers_arxiv = search_arxiv(query)
    # papers_scholar = search_semantic_scholar(query)
    
    papers = []
    papers.extend(papers_arxiv)  
    # papers.extend(papers_scholar)
    state['raw_papers'] = papers
    return state 
