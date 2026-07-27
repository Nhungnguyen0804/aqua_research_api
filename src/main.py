import time, json
import uuid
import threading

from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.schema import TopicRequest
from src.state import LitState
from src.graph import lit_agent_graph
import collections
import collections.abc
if not hasattr(collections, 'Sequence'):
    collections.Sequence = collections.abc.Sequence

import os
os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TORCH_HOME"] = "/tmp/torch"
app = FastAPI(title="Aqua Research AI API")

# Cho phép FE chạy port nào cx gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000" ,"https://nhungnguyen0804.github.io"], 
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

def format_sse_message(event_type: str, data: dict) -> str:
    # format SSE: "event: ...\ndata: ...\n\n"
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"

# chỗ lưu tạm thông tin các job đang chạy
# dict luu tam trong RAM sv 
# key la job id, value la trang thai + cac buoc da xong 
jobs = {}

# hàm pipeline chay trong 1 thread rieng  
# ko nam trong http nao, chạy độc lập 
# chạy xong cái nào thì ghi ket quả vào jobs[job_id][step]

def run_pipeline_in_background(job_id: str, topic: str):
    start_time = time.time()
    last_step_time = start_time
 
    try:
        state = make_initial_state(topic)
 
        # chay trong thread riêng 
        for event in lit_agent_graph.stream(state, stream_mode="updates"):
            node_name, node_update = next(iter(event.items()))
            now = time.time()
 
            step_number = NODE_ORDER.index(node_name) + 1 if node_name in NODE_ORDER else None
            total_steps = len(NODE_ORDER)
 
            step_result = {
                "node": node_name,
                "step": step_number,
                "total_steps": total_steps,
                "percent": round(step_number / total_steps * 100) if step_number else None,
                "elapsed_node_seconds": round(now - last_step_time, 2),
                "elapsed_total_seconds": round(now - start_time, 2),
                "data": to_jsonable(node_update),
            }
            last_step_time = now
 
            # ghi kết quả bước này vào bộ nhớ job, để endpoint stream đọc được
            jobs[job_id]["steps"].append(step_result)
 
        jobs[job_id]["status"] = "done"
 
    except Exception as error:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error_message"] = str(error)


# endpoint trả lời ngay ko chờ 
# tạo jobid, mở 1 thread chạy nền, trả job id về cho client 
@app.post("/api/run")
def run_pipeline(payload: TopicRequest):
    if not payload.topic.strip():
        raise HTTPException(status_code=400, detail="Topic không được để trống")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "running",
        "steps": [],
        "error_message": None,
    }
 
    # daemon=True để thread tự tắt theo server, không bị treo lại
    background_thread = threading.Thread(
        target=run_pipeline_in_background,
        args=(job_id, payload.topic),
        daemon=True,
    )
    background_thread.start()
 
    return {"job_id": job_id}


# endpoint theo doi tien do, cho dung sse 
# liên tục đọc jobs[job_id]["steps"] va gui buoc moi cho client 
@app.get("/api/stream/{job_id}")
def stream_job_progress(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Không tìm thấy job này")
 
    def event_generator():
        number_of_steps_already_sent = 0
 
        while True:
            job = jobs[job_id]
 
            # gửi các bước mới kể từ lần gửi trước
            new_steps = job["steps"][number_of_steps_already_sent:]
            for step in new_steps:
                yield format_sse_message("node_done", step)
            number_of_steps_already_sent = len(job["steps"])
 
            if job["status"] == "done":
                yield format_sse_message("done", {"message": "Pipeline chạy xong"})
                break
 
            if job["status"] == "error":
                yield format_sse_message("error", {"message": job["error_message"]})
                break
 
            # dòng yield trả ra này để giữ kết nối sống (keep-alive),
            # tránh bị proxy/gateway tự ngắt
            yield ": keep-alive\n\n"
            time.sleep(1)
 
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache","X-Accel-Buffering": "no",},
    )