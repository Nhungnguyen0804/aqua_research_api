from typing import TypedDict, List, Optional,Annotated

class LitState(TypedDict):
    query: str
    raw_papers: List[dict]

