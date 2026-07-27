
from pydantic import BaseModel

from src.state import LitState
from src.nodes.rq_pico import rq_pico_node

from langgraph.graph import StateGraph, START, END
from src.graph import lit_agent_graph




class TopicRequest(BaseModel):
    topic: str



@app.post("/api/pico")
#nhận topic
def get_pico(payload: TopicRequest):
    if not payload.topic or not payload.topic.strip():
        raise HTTPException(status_code=400, detail="Topic không được để trống")

    # State khởi tạo, chỉ cần điền topic, các field khác để rỗng/None
    state: LitState = {
        "topic": payload.topic,
        "pico": None,
        "sub_queries": [],
        "raw_papers": [],
        "deduped_papers": [],
        "screened_papers": [],
        "eligibility_criteria": None,
        "eligible_papers": [],
        "included_papers": [],
        "reviewed_papers": [],
        "synthesis": None,
        "report_path": None,
    }

    # Chỉ chạy 1 node duy nhất: rq_pico_node
    result_state = rq_pico_node(state)

    return {"pico": result_state["pico"]}



