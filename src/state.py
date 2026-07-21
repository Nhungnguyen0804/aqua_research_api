from typing import TypedDict, List, Optional,Annotated
from src.schema import PICO,EligibilityCriteria
# dữ liệu chạy xuyên suốt


class LitState(TypedDict):
    topic: str
    pico: PICO # research question
    sub_queries: list[str]
    raw_papers: List[dict]
    deduped_papers: List[dict]
    screened_papers: List[dict]
    eligibility_criteria: EligibilityCriteria
    eligible_papers: List[dict]
    included_papers: List[dict]
    reviewed_papers: List[dict]
    


