import time, json
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.schema import TopicRequest
from src.state import LitState
from src.graph import lit_agent_graph
import os
os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TORCH_HOME"] = "/tmp/torch"
app = FastAPI(title="Aqua Research AI API")

# Cho phép FE chạy port nào cx gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NODE_ORDER = [
    "research_question_node",
    "query_expansion_node",
    "search_node",
    "dedup_node",
    "screen_node",
    "criteria_node",
    "eligibility_node",
    "extract_node",
    "reviewer_node",
    "synthesize_node",
    "report_node",
]

def to_jsonable(obj):
    """Chuyển Pydantic model / dict / list lồng nhau thành json."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    return obj

def make_initial_state(topic: str) -> LitState:
    return {
        "topic": topic,
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
        "report_content": None,
    }

def sse(event_type: str, data: dict) -> str:
    # format SSE: "event: ...\ndata: ...\n\n"
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


@app.post("/api/run")
def run_pipeline(payload: TopicRequest):
    if not payload.topic.strip():
        raise HTTPException(status_code=400, detail="Topic không được để trống")

    state = make_initial_state(payload.topic)
    total = len(NODE_ORDER)

    def event_generator():
        t_start = time.time()
        t_last = t_start
        try:
            for event in lit_agent_graph.stream(state, stream_mode="updates"):
                node_name, node_update = next(iter(event.items()))
                now = time.time()
                idx = NODE_ORDER.index(node_name) + 1 if node_name in NODE_ORDER else None
                payload_out = {
                    "node": node_name,
                    "step": idx,
                    "total_steps": total,
                    "percent": round(idx / total * 100),
                    "elapsed_node_seconds": round(now - t_last, 2),
                    "elapsed_total_seconds": round(now - t_start, 2),
                    "data": to_jsonable(node_update), # update state vs json data => fe render 
                }
                t_last = now
                yield sse("node_done", payload_out)

            yield sse("done", {"elapsed_total_seconds": round(time.time() - t_start, 2)})
        except Exception as e:
            yield sse("error", {"message": str(e)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")

