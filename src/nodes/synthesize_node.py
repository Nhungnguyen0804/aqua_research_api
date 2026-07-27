from src.state import LitState
from src.schema import SynthesisResult
from src.prompt import build_synthesis_prompt
from src.services.llm import invoke_gemini
import json

def synthesize_node(state: LitState) -> LitState:
    reviewed_papers = state.get("reviewed_papers", [])
    # chỉ lấy paper "grounded" (extract đúng) để synthesis sạch
    good_papers = [p for p in reviewed_papers if p.get("review_status") == "grounded"]
    if not good_papers:
        good_papers = reviewed_papers  # fallback 

    print(f"[synthesize] đang tổng hợp từ {len(good_papers)} papers...")
    messages = build_synthesis_prompt(good_papers)
    result = invoke_gemini(messages, SynthesisResult)

    state["synthesis"] = result.model_dump()

    with open("data/topic_dir/synthesis.json", "w", encoding="utf-8") as f:
        json.dump(state["synthesis"], f, ensure_ascii=False, indent=2)

    print(f"[synthesize] xong. {len(result.themes)} themes, {len(result.gaps)} gaps")
    return state