from typing import TypedDict, List, Optional,Annotated

class LitState(TypedDict):
    query: str
    sub_queries: list[str]
    raw_papers: List[dict]
    deduped_papers: List[dict]
