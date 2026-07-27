from typing import TypedDict, List, Optional,Annotated, Any 
from src.schema import PICO,EligibilityCriteria,SynthesisResult
# dữ liệu chạy xuyên suốt


class LitState(TypedDict):
    topic: str
    pico: Optional[PICO] # research question
    sub_queries: list[str]
    raw_papers: List[dict]
    deduped_papers: List[dict]
    screened_papers: List[dict]
    eligibility_criteria: Optional[EligibilityCriteria]
    eligible_papers: List[dict]
    included_papers: List[dict] # extract node
    reviewed_papers: List[dict]
    synthesis: Optional[SynthesisResult]
    report_content: str 



