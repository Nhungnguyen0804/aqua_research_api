import json
from src.services.llm import invoke_gemini
from src.prompt.query_expansion import build_query_expansion_prompt
from src.utils import parse_json_response
def query_expansion_node(state):
    messages = build_query_expansion_prompt(state["query"])
    try:
        response = invoke_gemini(messages)
        print(type(response))
        print(type(response.content))
        print(repr(response.content))

        response_text = response.content
    except Exception as e:
        print(f"[filter] Gemini call thất bại hoàn toàn: {e} -> giữ tất cả bài trong batch")
        return [True] * len(response_text)
    json_response = parse_json_response(response_text)
    sub_queries = json.loads(json_response)

    return {"sub_queries": sub_queries}