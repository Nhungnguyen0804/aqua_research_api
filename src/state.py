from typing import TypedDict, List, Optional,Annotated
from src.schema import PICO
# dữ liệu chạy xuyên suốt


class LitState(TypedDict):
    topic: str
    research_question: PICO
    sub_queries: list[str]
    raw_papers: List[dict]
    deduped_papers: List[dict]
    filtered_papers: List[dict]


